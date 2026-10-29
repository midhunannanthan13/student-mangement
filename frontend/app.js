// =====================================================================
// 1. API ADDRESS  (the ONLY line you change after deploying)
// =====================================================================
const LOCAL_API_URL = "http://127.0.0.1:8000/api/students/";

// After you deploy the backend on Vercel, paste its address here.
// Keep the "/api/students/" at the end.
const PRODUCTION_API_URL = "https://YOUR-BACKEND.vercel.app/api/students/";

// On your computer (Live Server) use the local backend.
// On the internet (Vercel) use the production backend.
const isLocal = ["localhost", "127.0.0.1", ""].includes(window.location.hostname);
const API_URL = isLocal ? LOCAL_API_URL : PRODUCTION_API_URL;


// =====================================================================
// 2. PAGE ELEMENTS
// =====================================================================
const form      = document.getElementById("studentForm");
const table     = document.getElementById("studentTable");
const search    = document.getElementById("search");
const message   = document.getElementById("message");
const submitBtn = document.getElementById("submitBtn");
const cancelBtn = document.getElementById("cancelBtn");

let allStudents = [];     // every student loaded from the server
let editingId   = null;   // null = adding, number = editing that student


// =====================================================================
// 3. MESSAGES
// =====================================================================
function showMessage(text, type) {
    message.textContent = text;
    message.className = "message " + type;   // "success" or "error"
    message.hidden = false;
}

function hideMessage() {
    message.hidden = true;
}

// Shown when the backend answers but cannot use its database (HTTP 5xx)
function serverMessage(status) {
    return "The server could not use its database (error " + status + "). " +
           "If you use a free Aiven database it may be powered off: open the Aiven console and power it on, then try again.";
}

// Turns {"email": ["student with this email already exists."]} into readable text
function formatErrors(data) {
    return Object.entries(data)
        .map(([field, problems]) => `${field}: ${[].concat(problems).join(" ")}`)
        .join("  |  ");
}


// =====================================================================
// 4. GET: load students from Django
// =====================================================================
async function loadStudents() {
    if (API_URL.includes("YOUR-BACKEND")) {
        showMessage("Set PRODUCTION_API_URL in app.js to your backend address.", "error");
        return;
    }

    try {
        const response = await fetch(API_URL);

        if (response.status >= 500) {
            showMessage(serverMessage(response.status), "error");
            return;
        }

        if (!response.ok) {
            throw new Error("Server answered with status " + response.status);
        }

        allStudents = await response.json();
        showStudents();

    } catch (error) {
        showMessage("Cannot reach the backend. Is it running? (" + error.message + ")", "error");
    }
}


// =====================================================================
// 5. DISPLAY: search + draw the table
// =====================================================================
function showStudents() {
    const text = search.value.trim().toLowerCase();

    const matches = allStudents.filter(student =>
        student.name.toLowerCase().includes(text) ||
        student.email.toLowerCase().includes(text) ||
        student.course.toLowerCase().includes(text)
    );

    displayStudents(matches);
}

function displayStudents(students) {
    table.innerHTML = "";

    if (students.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 6;
        cell.className = "empty";
        cell.textContent = "No students found.";
        row.appendChild(cell);
        table.appendChild(row);
        return;
    }

    students.forEach(student => {
        const row = document.createElement("tr");

        // textContent (not innerHTML) so a name like <script> can never run as code
        [student.id, student.name, student.email, student.course, student.age].forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        const actions = document.createElement("td");

        const editBtn = document.createElement("button");
        editBtn.textContent = "Edit";
        editBtn.className = "btn-edit";
        editBtn.addEventListener("click", () => startEdit(student));

        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Delete";
        deleteBtn.className = "btn-delete";
        deleteBtn.addEventListener("click", () => deleteStudent(student.id));

        actions.append(editBtn, deleteBtn);
        row.appendChild(actions);
        table.appendChild(row);
    });
}

search.addEventListener("input", showStudents);


// =====================================================================
// 6. POST (add) and PUT (update)
// =====================================================================
form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const student = {
        name:   document.getElementById("name").value.trim(),
        email:  document.getElementById("email").value.trim(),
        course: document.getElementById("course").value.trim(),
        age:    Number(document.getElementById("age").value)
    };

    const isEditing = editingId !== null;
    const url       = isEditing ? `${API_URL}${editingId}/` : API_URL;
    const method    = isEditing ? "PUT" : "POST";

    try {
        const response = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(student)
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
            showMessage(isEditing ? "Student updated successfully." : "Student added successfully.", "success");
            resetForm();
            loadStudents();
        } else if (response.status >= 500) {
            showMessage(serverMessage(response.status), "error");
        } else {
            showMessage(formatErrors(data), "error");
        }

    } catch (error) {
        showMessage("Cannot reach the backend. Is it running?", "error");
    }
});


// =====================================================================
// 7. EDIT: fill the form with the chosen student
// =====================================================================
function startEdit(student) {
    editingId = student.id;

    document.getElementById("name").value   = student.name;
    document.getElementById("email").value  = student.email;
    document.getElementById("course").value = student.course;
    document.getElementById("age").value    = student.age;

    submitBtn.textContent = "Update Student";
    cancelBtn.hidden = false;
    hideMessage();
    form.scrollIntoView({ behavior: "smooth" });
}

function resetForm() {
    editingId = null;
    form.reset();
    submitBtn.textContent = "Add Student";
    cancelBtn.hidden = true;
}

cancelBtn.addEventListener("click", function () {
    resetForm();
    hideMessage();
});


// =====================================================================
// 8. DELETE
// =====================================================================
async function deleteStudent(id) {
    if (!confirm("Delete this student?")) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}${id}/`, { method: "DELETE" });

        if (response.ok) {
            if (editingId === id) {
                resetForm();
            }
            showMessage("Student deleted successfully.", "success");
            loadStudents();
        } else if (response.status >= 500) {
            showMessage(serverMessage(response.status), "error");
        } else {
            showMessage("Could not delete the student.", "error");
        }

    } catch (error) {
        showMessage("Cannot reach the backend. Is it running?", "error");
    }
}


// =====================================================================
// 9. START
// =====================================================================
loadStudents();
