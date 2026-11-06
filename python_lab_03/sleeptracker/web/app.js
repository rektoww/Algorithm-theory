
const recordsBody = document.getElementById("recordsBody");
const refreshButton = document.getElementById("refreshButton");
const message = document.getElementById("message");

const recordForm = document.getElementById("recordForm");
const formTitle = document.getElementById("formTitle");
const formMessage = document.getElementById("formMessage");

const fellAsleepInput = document.getElementById("fellAsleep");
const wokeUpInput = document.getElementById("wokeUp");
const qualityInput = document.getElementById("quality");
const notesInput = document.getElementById("notes");

const saveButton = document.getElementById("saveButton");
const cancelEditButton = document.getElementById("cancelEditButton");

let editingRecordId = null;
let sleepChart = null;


async function apiRequest(path, options = {}) {
    const response = await fetch(path, options);

    if (!response.ok) {
        let errorMessage = `Ошибка HTTP ${response.status}`;

        try {
            const data = await response.json();

            if (typeof data.detail === "string") {
                errorMessage = data.detail;
            } else if (Array.isArray(data.detail)) {
                errorMessage = data.detail
                    .map(error => error.msg)
                    .join("; ");
            }
        } catch {
        }

        throw new Error(errorMessage);
    }

    if (response.status === 204) {
        return null;
    }

    return await response.json();
}


function formatDateTime(date) {
    const pad = value => String(value).padStart(2, "0");

    const year = date.getFullYear();
    const month = pad(date.getMonth() + 1);
    const day = pad(date.getDate());
    const hours = pad(date.getHours());
    const minutes = pad(date.getMinutes());

    return `${year}-${month}-${day}T${hours}:${minutes}`;
}


function formatMinutes(minutes) {
    if (minutes === null || minutes === undefined) {
        return "—";
    }

    const total = Math.round(minutes);
    const hours = Math.floor(total / 60);
    const remaining = total % 60;

    return `${hours} ч ${remaining} мин`;
}


function resetForm() {
    editingRecordId = null;

    formTitle.textContent = "Новая запись";
    saveButton.textContent = "Добавить запись";
    cancelEditButton.hidden = true;

    const now = new Date();
    const asleep = new Date(
        now.getTime() - 8 * 60 * 60 * 1000
    );

    fellAsleepInput.value = formatDateTime(asleep);
    wokeUpInput.value = formatDateTime(now);

    qualityInput.value = "4";
    notesInput.value = "";

    formMessage.textContent = "";
}


function addCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value ?? "";

    row.appendChild(cell);
}


async function loadRecords() {
    try {
        const records = await apiRequest("/records");

        recordsBody.replaceChildren();

        for (const record of records) {
            const row = document.createElement("tr");

            const minutes = record.duration_minutes;
            const duration =
                `${Math.floor(minutes / 60)} ч ${minutes % 60} мин`;

            addCell(row, record.record_id);

            addCell(
                row,
                record.fell_asleep_at.slice(0, 16)
                    .replace("T", " ")
            );

            addCell(
                row,
                record.woke_up_at.slice(0, 16)
                    .replace("T", " ")
            );

            addCell(row, duration);
            addCell(row, `${record.quality}/5`);
            addCell(row, record.notes);

            const actionsCell = document.createElement("td");
            const actions = document.createElement("div");

            actions.className = "table-actions";

            const editButton = document.createElement("button");
            editButton.textContent = "Изменить";

            editButton.addEventListener("click", () => {
                startEditing(record.record_id);
            });

            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Удалить";
            deleteButton.className = "delete-button";

            deleteButton.addEventListener("click", () => {
                deleteRecord(record.record_id);
            });

            actions.append(editButton, deleteButton);
            actionsCell.appendChild(actions);
            row.appendChild(actionsCell);

            recordsBody.appendChild(row);
        }

        message.textContent = records.length === 0
            ? "Записей пока нет"
            : `Всего записей: ${records.length}`;

    } catch (error) {
        message.textContent = error.message;
    }
}


async function startEditing(recordId) {
    try {
        const record = await apiRequest(
            `/records/${recordId}`
        );

        editingRecordId = recordId;

        formTitle.textContent =
            `Редактирование записи №${recordId}`;

        saveButton.textContent = "Сохранить изменения";
        cancelEditButton.hidden = false;

        fellAsleepInput.value =
            record.fell_asleep_at.slice(0, 16);

        wokeUpInput.value =
            record.woke_up_at.slice(0, 16);

        qualityInput.value = record.quality;
        notesInput.value = record.notes;

        formMessage.textContent = "";

        recordForm.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    } catch (error) {
        formMessage.textContent = error.message;
    }
}


async function saveRecord(event) {
    event.preventDefault();

    const asleep = fellAsleepInput.value;
    const wakeUp = wokeUpInput.value;

    if (new Date(wakeUp) <= new Date(asleep)) {
        formMessage.textContent =
            "Пробуждение должно быть позже засыпания";
        return;
    }

    const data = {
        fell_asleep_at: asleep,
        woke_up_at: wakeUp,
        quality: Number(qualityInput.value),
        notes: notesInput.value.trim()
    };

    const isEditing = editingRecordId !== null;

    const path = isEditing
        ? `/records/${editingRecordId}`
        : "/records";

    const method = isEditing ? "PUT" : "POST";

    saveButton.disabled = true;

    try {
        await apiRequest(path, {
            method: method,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        resetForm();
        await loadRecords();

        formMessage.textContent = isEditing
            ? "Изменения успешно сохранены!"
            : "Запись успешно добавлена!";

        await loadStatistics();
        await loadActivityLog();

    } catch (error) {
        formMessage.textContent = error.message;

    } finally {
        saveButton.disabled = false;
    }
}


async function deleteRecord(recordId) {
    const confirmed = confirm(
        `Удалить запись №${recordId}?`
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(`/records/${recordId}`, {
            method: "DELETE"
        });

        if (editingRecordId === recordId) {
            resetForm();
        }

        await loadRecords();
        await loadStatistics();
        await loadActivityLog();

        formMessage.textContent =
            `Запись №${recordId} удалена`;

    } catch (error) {
        formMessage.textContent = error.message;
    }
}


async function loadStatistics() {
    const statisticsMessage =
        document.getElementById("statisticsMessage");

    try {
        const stats = await apiRequest("/statistics");

        document.getElementById("recordCount")
            .textContent = stats.record_count;

        document.getElementById("averageDuration")
            .textContent = formatMinutes(
                stats.average_duration_minutes
            );

        document.getElementById("minDuration")
            .textContent = formatMinutes(
                stats.shortest_duration_minutes
            );

        document.getElementById("maxDuration")
            .textContent = formatMinutes(
                stats.longest_duration_minutes
            );

        const days = stats.duration_by_day.slice(-14);

        const labels = days.map(item => {
            const date = item.date;
            return `${date.slice(8, 10)}.${date.slice(5, 7)}`;
        });

        const hours = days.map(
            item => item.duration_minutes / 60
        );

        if (sleepChart !== null) {
            sleepChart.destroy();
        }

        sleepChart = new Chart(
            document.getElementById("sleepChart"),
            {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Продолжительность сна, ч",
                        data: hours,
                        backgroundColor: "#546e7a",
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Часы"
                            }
                        }
                    }
                }
            }
        );

        statisticsMessage.textContent =
            days.length === 0
                ? "Данных для графика пока нет"
                : "";

    } catch (error) {
        statisticsMessage.textContent = error.message;
    }
}


async function loadActivityLog() {
    const activityBody = document.getElementById("activityBody");
    const activityMessage = document.getElementById("activityMessage");

    try {
        const events = await apiRequest("/activity-log");

        activityBody.replaceChildren();

        const actionNames = {
            created: "Добавление",
            updated: "Изменение",
            deleted: "Удаление"
        };

        for (const event of events) {
            const row = document.createElement("tr");

            const date = new Date(event.created_at);

            const formattedDate = Number.isNaN(date.getTime())
                ? event.created_at.replace("T", " ").slice(0, 16)
                : date.toLocaleString("ru-RU", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit"
                });

            addCell(row, formattedDate);
            addCell(
                row,
                actionNames[event.action] ?? event.action
            );
            addCell(row, event.record_id ?? "—");
            addCell(row, event.details);

            activityBody.appendChild(row);
        }

        activityMessage.textContent = events.length === 0
            ? "История действий пока пуста"
            : `Всего событий: ${events.length}`;

    } catch (error) {
        activityMessage.textContent = error.message;
    }
}

refreshButton.addEventListener("click", loadRecords);
recordForm.addEventListener("submit", saveRecord);
cancelEditButton.addEventListener("click", resetForm);

document.getElementById("refreshStatisticsButton").addEventListener("click", loadStatistics);

document.getElementById("refreshActivityButton").addEventListener("click", loadActivityLog);

resetForm();
loadRecords();
loadStatistics();
loadActivityLog();