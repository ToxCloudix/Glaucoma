document.addEventListener("DOMContentLoaded", async () => {
    const searchBar = document.getElementById("search-bar");
    const patientList = document.getElementById("patient-list");
    const sortOrderSelect = document.getElementById("sort-order");
    const patientModal = document.getElementById("patient-modal");
    const modalCloseButton = patientModal.querySelector(".close-button");
    const patientImagesTable = document.getElementById("patient-images-table").querySelector("tbody");
    const uploadForm = document.getElementById("upload-image-form");

    /**
     * Загружает список пациентов с сервера и отображает их.
     * @param {string} query - строка поиска.
     * @param {string} sortBy - параметр сортировки.
     */
    async function loadPatients(query = "", sortBy = "last_name") {
        try {
            const response = await fetch(`/glaucoma/patients/?search=${encodeURIComponent(query)}&sort_by=${sortBy}`);
            if (response.ok) {
                const patients = await response.json();
                patientList.innerHTML = ""; // Очищаем список перед добавлением новых пациентов

                patients.forEach(patient => {
                    const li = document.createElement("li");
                    li.innerHTML = `<a href="#" data-id="${patient.id}">${patient.name}</a>`;
                    patientList.appendChild(li);
                });

                // Привязываем событие клика к каждому элементу
                patientList.querySelectorAll("a").forEach(link => {
                    link.addEventListener("click", (event) => {
                        event.preventDefault();
                        const patientId = event.target.dataset.id;
                        loadPatientDetails(patientId);
                    });
                });
            } else {
                console.error("Failed to fetch patients.");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }

    /**
     * Загружает детали пациента и отображает их в модальном окне.
     * @param {number} patientId - ID пациента.
     */
    async function loadPatientDetails(patientId) {
        try {
            const response = await fetch(`/glaucoma/patients/${patientId}/`);
            if (response.ok) {
                const data = await response.json();

                // Заполняем поля модального окна
                document.getElementById("patient-first-name").innerText = data.first_name;
                document.getElementById("patient-last-name").innerText = data.last_name;
                document.getElementById("patient-gender").innerText = data.gender;
                document.getElementById("patient-age").innerText = data.age;

                // Устанавливаем ID пациента в атрибут data-id
                document.getElementById("patient-first-name").dataset.id = patientId;

                // Загружаем изображения пациента
                loadPatientImages(patientId);

                // Отображаем модальное окно
                patientModal.style.display = "block";
            } else {
                console.error("Failed to fetch patient details.");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }

    /**
     * Загружает изображения пациента и отображает их в таблице.
     * @param {number} patientId - ID пациента.
     */
    async function loadPatientImages(patientId) {
        try {
            const response = await fetch(`/glaucoma/patients/${patientId}/images/`);
            if (response.ok) {
                const images = await response.json();
                patientImagesTable.innerHTML = ""; // Очищаем таблицу перед добавлением новых данных

                images.forEach(image => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${image.date_taken}</td>
                        <td>${image.eye}</td>
                        <td>
                            <a href="/glaucoma/image/analysis/${image.id}">
                                <img src="${image.image}" alt="Eye Image" width="100">
                            </a>
                        </td>
                    `;
                    patientImagesTable.appendChild(row);
                });
            } else {
                console.error("Failed to fetch patient images.");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }

    // Обработчик отправки формы загрузки изображения
    uploadForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(uploadForm);
        const patientId = document.getElementById("patient-first-name").dataset.id; // ID текущего пациента

        if (!patientId) {
            alert("Patient ID not found!");
            return;
        }

        try {
            const response = await fetch(`/glaucoma/patients/${patientId}/upload_image/`, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                alert("Image uploaded successfully!");
                loadPatientImages(patientId); // Обновляем таблицу изображений
            } else {
                alert("Failed to upload image.");
            }
        } catch (error) {
            console.error("Error uploading image:", error);
        }
    });

    // Закрытие модального окна
    modalCloseButton.addEventListener("click", () => {
        patientModal.style.display = "none";
    });

    // Начальная загрузка списка пациентов
    loadPatients();

    // Фильтрация и сортировка
    searchBar.addEventListener("input", () => loadPatients(searchBar.value, sortOrderSelect.value));
    sortOrderSelect.addEventListener("change", () => loadPatients(searchBar.value, sortOrderSelect.value));
});
