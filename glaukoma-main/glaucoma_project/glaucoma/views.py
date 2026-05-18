
import json
import logging
import cv2
import numpy as np
import scipy
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Используем неинтерактивный backend
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q  # Импортируем Q для комбинирования условий фильтрации
from django.utils import timezone

from glaucoma.models import Doctor, Patient, PatientImage, DoctorImageAnalysis
from glaucoma.serializers import PatientImageSerializer
from .cd import segment, cdr, crop_to_roi

logger = logging.getLogger(__name__)


def doctor_list_view(request):
    # Получаем всех врачей из таблицы Doctor
    doctors = Doctor.objects.all()
    return render(request, 'doctor_list.html', {'doctors': doctors})


def logout_view(request):
    request.session.flush()  # Удалить все данные сессии
    return redirect('/login/')

@login_required
def home_page(request):
    return render(request, 'glaucoma/home.html')


@login_required
def patient_list_view(request):
    # Получаем строку поиска из запроса
    search_query = request.GET.get('search', '').lower()  # Преобразуем запрос в нижний регистр
    sort_by = request.GET.get('sort_by', 'last_name')  # По умолчанию сортировка по фамилии

    # Если нет строки поиска, возвращаем всех пациентов
    if search_query:
        # Используем Q для поиска по имени и фамилии одновременно, фильтруем только по началу строки
        patients = Patient.objects.filter(
            Q(first_name__istartswith=search_query) | Q(last_name__istartswith=search_query)
        )
    else:
        patients = Patient.objects.all()  # Если ничего не введено, показываем всех пациентов

    # Сортировка в зависимости от выбранного параметра
    if sort_by == 'first_name':
        patients = patients.order_by('first_name', 'last_name')  # Сортировка по имени
    else:
        patients = patients.order_by('last_name', 'first_name')  # Сортировка по фамилии

    # Собираем данные о пациентах в список
    patient_data = [
        {"id": patient.id, 
         "name": f"{patient.first_name} {patient.last_name}" if sort_by == 'first_name' 
                 else f"{patient.last_name} {patient.first_name}"}
        for patient in patients
    ]
    
    # Возвращаем данные в формате JSON
    return JsonResponse(patient_data, safe=False)

@login_required
def get_patient_details(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    data = {
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "gender": patient.gender,
        "age": (timezone.now().date() - patient.date_of_birth).days // 365,
    }
    return JsonResponse(data)

@csrf_exempt
@login_required
def upload_patient_image(request, patient_id):
    if request.method == "POST":
        patient = get_object_or_404(Patient, id=patient_id)
        date_taken = request.POST.get("date")
        eye = request.POST.get("eye")
        image_file = request.FILES["image"]
        image_data = image_file.read()

        PatientImage.objects.create(
            patient=patient,
            date_taken=date_taken,
            eye=eye,
            image=image_file
        )
        return JsonResponse({"message": "Image uploaded successfully!"})
    return JsonResponse({"error": "Invalid request method."}, status=400)

@login_required
def patient_images_view(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    images = patient.images.all()
    serialized_data = PatientImageSerializer(images, many=True).data

    return JsonResponse(serialized_data, safe=False)

@login_required
def image_analysis(request, image_id):
    image = get_object_or_404(PatientImage, id=image_id)
    
    if request.user.is_superuser:
        doctor_instance = Doctor.objects.first()
    else:
        # Предполагается, что у врача настроена связь OneToOne (request.user.doctor)
        if not hasattr(request.user, 'doctor') or not request.user.groups.filter(name='doctor').exists():
            return redirect(request.META.get('HTTP_REFERER', '/'))
        doctor_instance = request.user.doctor

    analysis = DoctorImageAnalysis.objects.filter(
        patient_image=image,
        doctor=doctor_instance
    ).last()


    if request.method == "POST" and request.POST.get('action') == 'segment':
        img_path = image.image.path
        img = cv2.imread(img_path)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(10, 10))
        
        Abo, Ago, Aro = cv2.split(img)
        Aro = clahe.apply(Aro)
        
        M = 60
        filter = scipy.signal.windows.gaussian(M, std=6)
        STDf = filter.std()
        
        Ar = Aro - Aro.mean() - Aro.std()
        Mr = Ar.mean()
        SDr = Ar.std()
        Thr = 0.5*M - STDf - SDr
        
        M = 20
        filter_cup = scipy.signal.windows.gaussian(M, std=6)
        STDf = filter_cup.std()
        
        Ag = Ago - Ago.mean() - Ago.std()
        Mg = Ag.mean()
        SDg = Ag.std()
        Thg = 0.5*M + 2*STDf + 2*SDg + Mg
        
        # Optic Disk segmentation
        Dd = np.where(Ar > Thr, 255, 0).astype(np.uint8)
        Dc = np.where(Ag > Thg, 255, 0).astype(np.uint8)
        
        # Convert images to base64 for returning to frontend
        def img_to_base64(img_array):
            _, buffer = cv2.imencode('.png', img_array)
            return base64.b64encode(buffer).decode('utf-8')
        
        response = {
            'disk': img_to_base64(Dd),
            'cup': img_to_base64(Dc)
        }
        return JsonResponse(response)
    
    analysis_data = None
    if analysis:
        analysis_data = {
            "notes": analysis.notes,
            "description": analysis.description,
            "cdr": analysis.cdr,
            "cdr_points": analysis.cdr_points,
            # Если нужно, можно добавить другие поля:
            # "updated_at": analysis.updated_at.isoformat() 
            # и т.д.
        }

    age = (timezone.now().date() - image.patient.date_of_birth).days // 365
    context = {
        'image': image,
        'patient': image.patient,
        'age': age,
        'analysis': analysis,
        'analysis_data': analysis_data,
    }
    return render(request, 'glaucoma/image_analysis.html', context=context)


@login_required
def auto_cdr_view(request, image_id):
    # Получаем объект изображения
    image_obj = get_object_or_404(PatientImage, id=image_id)
    # Загружаем исходное изображение
    img = cv2.imread(image_obj.image.path)
    # Выполняем сегментацию без сохранения файлов; segment() возвращает (disk, cup)
    disk_img, cup_img = segment(img, plot_hist=False, plot_seg=False)
    # Вычисляем CDR, передавая сегментированные изображения, plot=False
    cdr_value, a, b = cdr(cup_img, disk_img, plot=False)
    return JsonResponse({'cdr': float(cdr_value)})

@login_required
def auto_segmentation_view(request, image_id):
    image_obj = get_object_or_404(PatientImage, id=image_id)
    # Загружаем исходное изображение
    img = cv2.imread(image_obj.image.path)
    img = crop_to_roi(img)
    orig_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Выполняем сегментацию без сохранения файлов; segment() возвращает (disk, cup)
    disk_img, cup_img = segment(img, plot_hist=False, plot_seg=False)
    _, Cc, Dd = cdr (cup_img, disk_img, plot=False)

    fig = plt.figure(figsize=(12, 8))
    gs = GridSpec(2, 3, figure=fig)

    ax_orig = fig.add_subplot(gs[:, 0])  # ":" по строкам => обе строки, 0 => первая колонка

    # Верхняя строка, колонки 1 и 2
    ax_disk = fig.add_subplot(gs[0, 1])
    ax_cup  = fig.add_subplot(gs[0, 2])
    
    # Нижняя строка, колонки 1 и 2
    ax_disk_morph = fig.add_subplot(gs[1, 1])
    ax_cup_morph  = fig.add_subplot(gs[1, 2])
    
    # 5) Заполняем подграфики
    #    (1) Original Image (на всю левую колонку, 2 строки)
    ax_orig.imshow(orig_rgb)
    ax_orig.set_title("Original Image")
    ax_orig.axis("off")
    
    #    (2) Optic Disk (вверх справа)
    ax_disk.imshow(disk_img, cmap='gray')
    ax_disk.set_title("Optic Disk")
    ax_disk.axis("off")

    #    (3) Optic Cup (вверх справа, третий столбец)
    ax_cup.imshow(cup_img, cmap='gray')
    ax_cup.set_title("Optic Cup")
    ax_cup.axis("off")

    #    (4) Disk Morph (внизу, второй столбец)
    ax_disk_morph.imshow(Dd, cmap='gray')
    ax_disk_morph.set_title("Optic Disk")
    ax_disk_morph.axis("off")

    #    (5) Cup Morph (внизу, третий столбец)
    ax_cup_morph.imshow(Cc, cmap='gray')
    ax_cup_morph.set_title("Optic Cup")
    ax_cup_morph.axis("off")


    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    encoded_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    return JsonResponse({'segmented_image': encoded_image})

@csrf_exempt
@login_required
def save_analysis_view(request, image_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            notes = data.get("notes", "")
            description = data.get("description", "")
            cdr_value = data.get("cdr", 0)
            cdr_points = data.get("cdr_points", None)

            if request.user.is_superuser:
                # Если пользователь админ, выбираем, например, первого доктора из базы.
                doctor_instance = Doctor.objects.first()
            else:
                # Если пользователь — доктор, предполагаем, что у него настроен OneToOneField с моделью Doctor.
                doctor_instance = request.user.doctor

            image_obj = get_object_or_404(PatientImage, id=image_id)
            # Проверяем, существует ли уже анализ для данного изображения и врача
            analysis, created = DoctorImageAnalysis.objects.get_or_create(
                patient_image=image_obj,
                doctor=doctor_instance,  # При условии, что request.user соответствует модели Doctor.
                defaults={
                    "notes": notes,
                    "description": description,
                    "cdr": cdr_value,
                    "cdr_points": cdr_points,
                }
            )
            if not created:
                # Если запись уже существует — обновляем её
                analysis.notes = notes
                analysis.description = description
                analysis.cdr = cdr_value
                analysis.cdr_points = cdr_points
                analysis.updated_at = timezone.now()
                analysis.save()

            return JsonResponse({"message": f"Анализ успешно сохранён! Доктор ID: {doctor_instance.id}"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Неверный метод запроса."}, status=400)

