document.addEventListener("DOMContentLoaded", function() {
    const messagesTable = document.getElementById("messagesTable").getElementsByTagName('tbody')[0];
    const searchInput = document.getElementById('search');

    // Fetch messages from the API
    fetch('https://prototipo-mqtt.onrender.com/mensajes')
        .then(response => response.json())
        .then(data => {
            data.forEach(mensaje => {
                let row = messagesTable.insertRow();
                let idCell = row.insertCell(0);
                let msgCell = row.insertCell(1);
                idCell.textContent = mensaje.id;
                msgCell.textContent = mensaje.mensaje;
            });
        })
        .catch(error => console.error('Error al obtener los mensajes:', error));

    // Search functionality
    searchInput.addEventListener('keyup', function() {
        const searchTerm = searchInput.value.toLowerCase();
        const rows = messagesTable.getElementsByTagName('tr');
        Array.from(rows).forEach(row => {
            const mensaje = row.cells[1].textContent.toLowerCase();
            if (mensaje.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
});
