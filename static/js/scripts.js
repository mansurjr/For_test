document.querySelectorAll('.attendance').forEach(select => {
    select.addEventListener('change', function () {
        let studentId = this.getAttribute('data-student');
        let attendance = this.value;
        let date = this.getAttribute('data-date');

        fetch("{% url 'update_attendance' %}", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": "{{ csrf_token }}"
            },
            body: JSON.stringify({ 
                student_id: studentId, 
                date: date,
                status: attendance
            })
        }).then(response => response.json()).then(data => {
            console.log(data);
        }).catch(error => console.error("Error:", error));
    });
});
