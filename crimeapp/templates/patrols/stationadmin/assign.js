// Sample data - replace with your actual data
const officers = [
    { id: 1, name: "Officer Smith", badge: "1234", status: "available", assignedCrimes: [] },
    { id: 2, name: "Officer Johnson", badge: "5678", status: "available", assignedCrimes: [] },
    { id: 3, name: "Officer Williams", badge: "9012", status: "available", assignedCrimes: [] }
];

const crimes = [
    { id: 1, type: "Theft", location: "Downtown", severity: "Medium", assignedOfficer: null },
    { id: 2, type: "Assault", location: "North District", severity: "High", assignedOfficer: null },
    { id: 3, type: "Vandalism", location: "South District", severity: "Low", assignedOfficer: null }
];

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    renderOfficers();
    renderCrimes();
});

function renderOfficers() {
    const container = document.getElementById('officers-container');
    container.innerHTML = '';
    
    officers.forEach(officer => {
        const card = document.createElement('div');
        card.className = `officer-card ${officer.status}`;
        card.innerHTML = `
            <h5>${officer.name}</h5>
            <p>Badge: ${officer.badge}</p>
            <p>Status: <span class="badge ${getStatusBadgeClass(officer.status)}">${officer.status}</span></p>
            <p>Assigned Crimes: ${officer.assignedCrimes.length}</p>
        `;
        container.appendChild(card);
    });
}

function renderCrimes() {
    const container = document.getElementById('crimes-container');
    container.innerHTML = '';
    
    crimes.forEach(crime => {
        const card = document.createElement('div');
        card.className = `crime-card ${crime.assignedOfficer ? 'assigned' : ''}`;
        card.dataset.id = crime.id;
        card.innerHTML = `
            <h5>${crime.type}</h5>
            <p>Location: ${crime.location}</p>
            <p>Severity: <span class="badge ${getSeverityBadgeClass(crime.severity)}">${crime.severity}</span></p>
            <p>${crime.assignedOfficer ? 'Assigned to: ' + getOfficerName(crime.assignedOfficer) : 'Click to assign'}</p>
        `;
        
        if (!crime.assignedOfficer) {
            card.addEventListener('click', () => assignCrime(crime.id));
        }
        
        container.appendChild(card);
    });
}

function getStatusBadgeClass(status) {
    return status === 'available' ? 'bg-success' : 'bg-warning';
}

function getSeverityBadgeClass(severity) {
    switch(severity.toLowerCase()) {
        case 'high': return 'bg-danger';
        case 'medium': return 'bg-warning';
        case 'low': return 'bg-success';
        default: return 'bg-secondary';
    }
}

function getOfficerName(id) {
    const officer = officers.find(o => o.id === id);
    return officer ? officer.name : 'Unknown';
}

function assignCrime(crimeId) {
    // Find available officer (simple algorithm - in reality you'd use your AI)
    const availableOfficer = officers.find(o => o.status === 'available');
    if (!availableOfficer) {
        alert('No available officers!');
        return;
    }
    
    // Update crime
    const crimeIndex = crimes.findIndex(c => c.id === crimeId);
    crimes[crimeIndex].assignedOfficer = availableOfficer.id;
    
    // Update officer
    const officerIndex = officers.findIndex(o => o.id === availableOfficer.id);
    officers[officerIndex].assignedCrimes.push(crimeId);
    
    // If officer has 3 crimes, mark as busy
    if (officers[officerIndex].assignedCrimes.length >= 3) {
        officers[officerIndex].status = 'busy';
    }
    
    // Re-render
    renderOfficers();
    renderCrimes();
}