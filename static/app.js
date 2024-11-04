document.addEventListener("DOMContentLoaded", function() {
    const messagesTable = document.getElementById("messagesTable").getElementsByTagName('tbody')[0];
    const searchInput = document.getElementById('search');
    let currentPage = 1;
    const limit = 10; // Limite de mensajes por página

    // Función para obtener mensajes con paginación
    function fetchMessages(page = 1) {
        fetch(`https://mqtt-mixto.onrender.com/mensajes?page=${page}&limit=${limit}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la red: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                messagesTable.innerHTML = ''; // Limpiar la tabla
                data.forEach(mensaje => {
                    let row = messagesTable.insertRow();
                    let idCell = row.insertCell(0);
                    let msgCell = row.insertCell(1);
                    idCell.textContent = mensaje.id;
                    msgCell.textContent = mensaje.mensaje;
                });
                currentPage = page; // Actualizar página actual
            })
            .catch(error => console.error('Error al obtener los mensajes:', error));
    }

    // Función para manejar la búsqueda
    searchInput.addEventListener('keyup', function() {
        const searchTerm = searchInput.value.toLowerCase();
        const rows = messagesTable.getElementsByTagName('tr');
        Array.from(rows).forEach(row => {
            const mensaje = row.cells[1].textContent.toLowerCase();
            row.style.display = mensaje.includes(searchTerm) ? '' : 'none';
        });
    });

    // Eventos de navegación
    document.getElementById('nextPage').addEventListener('click', () => fetchMessages(currentPage + 1));
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) fetchMessages(currentPage - 1);
    });

    // Cargar la primera página de mensajes al inicio
    fetchMessages();
});
