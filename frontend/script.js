// Configurações globais
const API_URL = 'http://localhost:8000';
let currentEditingWineId = null;

// Elementos DOM
const elements = {
    wineForm: document.getElementById('wineForm'),
    resultContainer: document.getElementById('resultContainer'),
    classificationResult: document.getElementById('classificationResult'),
    winesTableBody: document.getElementById('winesTableBody'),
    editModal: new bootstrap.Modal(document.getElementById('editModal')),
    saveChangesBtn: document.getElementById('saveChangesBtn'),
    editModalBody: document.getElementById('editModalBody')
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    loadWines();
    setupEventListeners();
    createLoader();
});

function setupEventListeners() {
    elements.wineForm.addEventListener('submit', handleFormSubmit);
    elements.saveChangesBtn.addEventListener('click', saveWineChanges);
}

// Funções principais
async function loadWines() {
    showLoading(true);
    try {
        const response = await fetch(`${API_URL}/vinhos`);
        if (!response.ok) return showErrorResponse(response);
        
        const wines = await response.json();
        renderWinesTable(wines);
    } catch (error) {
        showAlert('danger', `Erro: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();

    const documentoValue = document.getElementById('documento').value.trim();
    if (documentoValue.length < 11) {
        showAlert('danger', 'O campo Documento deve ter pelo menos 11 caracteres.');
        return;
    }

    showLoading(true);
    
    try {
        const formData = new FormData(elements.wineForm);
        const wineData = {
            nome: formData.get('nome'),
            fornecedor: formData.get('fornecedor'),
            documento: documentoValue,
            acidez_fixa: validateNumberInput(formData.get('acidez_fixa'), 'Acidez Fixa'),
            acidez_volatil: validateNumberInput(formData.get('acidez_volatil'), 'Acidez Volátil'),
            acido_citrico: validateNumberInput(formData.get('acido_citrico'), 'Ácido Cítrico'),
            acucar_residual: validateNumberInput(formData.get('acucar_residual'), 'Açúcar Residual'),
            cloretos: validateNumberInput(formData.get('cloretos'), 'Cloretos'),
            dioxido_enxofre_livre: validateNumberInput(formData.get('dioxido_enxofre_livre'), 'SO₂ Livre'),
            dioxido_enxofre_total: validateNumberInput(formData.get('dioxido_enxofre_total'), 'SO₂ Total'),
            densidade: validateNumberInput(formData.get('densidade'), 'Densidade'),
            ph: validateNumberInput(formData.get('ph'), 'pH'),
            sulfatos: validateNumberInput(formData.get('sulfatos'), 'Sulfatos'),
            teor_alcoolico: validateNumberInput(formData.get('teor_alcoolico'), 'Teor Alcoólico')
        };

        const response = await fetch(`${API_URL}/vinhos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(wineData)
        });

        if (!response.ok) return showErrorResponse(response);

        const result = await response.json();
        showClassificationResult(result.classificacao);
        elements.wineForm.reset();
        await loadWines();
    } catch (error) {
        showAlert('danger', `Erro: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

async function openEditModal(wineId) {
    showLoading(true);
    try {
        const response = await fetch(`${API_URL}/vinhos/${wineId}`);
        if (!response.ok) return showErrorResponse(response);
        
        const wine = await response.json();
        currentEditingWineId = wineId;
        renderEditForm(wine);
        elements.editModal.show();
    } catch (error) {
        showAlert('danger', `Erro: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

async function saveWineChanges() {
    const documentoValue = document.getElementById('editDocumento').value.trim();

    showLoading(true);
    try {
        const wineData = {
            nome: document.getElementById('editNome').value,
            fornecedor: document.getElementById('editFornecedor').value,
            documento: documentoValue,
            acidez_fixa: validateNumberInput(document.getElementById('editAcidezFixa').value, 'Acidez Fixa'),
            acidez_volatil: validateNumberInput(document.getElementById('editAcidezVolatil').value, 'Acidez Volátil'),
            acido_citrico: validateNumberInput(document.getElementById('editAcidoCitrico').value, 'Ácido Cítrico'),
            acucar_residual: validateNumberInput(document.getElementById('editAcucarResidual').value, 'Açúcar Residual'),
            cloretos: validateNumberInput(document.getElementById('editCloretos').value, 'Cloretos'),
            dioxido_enxofre_livre: validateNumberInput(document.getElementById('editDioxidoEnxofreLivre').value, 'SO₂ Livre'),
            dioxido_enxofre_total: validateNumberInput(document.getElementById('editDioxidoEnxofreTotal').value, 'SO₂ Total'),
            densidade: validateNumberInput(document.getElementById('editDensidade').value, 'Densidade'),
            ph: validateNumberInput(document.getElementById('editPh').value, 'pH'),
            sulfatos: validateNumberInput(document.getElementById('editSulfatos').value, 'Sulfatos'),
            teor_alcoolico: validateNumberInput(document.getElementById('editTeorAlcoolico').value, 'Teor Alcoólico')
        };

        const response = await fetch(`${API_URL}/vinhos/${currentEditingWineId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(wineData)
        });

        if (!response.ok) return showErrorResponse(response);

        elements.editModal.hide();
        showAlert('success', 'Vinho atualizado com sucesso!');
        await loadWines();
    } catch (error) {
        showAlert('danger', `Erro: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

async function deleteWine(wineId) {
    if (!confirm('Tem certeza que deseja excluir este vinho?')) return;
    
    showLoading(true);
    try {
        const response = await fetch(`${API_URL}/vinhos/${wineId}`, {
            method: 'DELETE'
        });

        if (!response.ok) return showErrorResponse(response);

        showAlert('success', 'Vinho excluído com sucesso!');
        await loadWines();
    } catch (error) {
        showAlert('danger', `Erro: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Funções auxiliares
function validateNumberInput(value, fieldName) {
    if (isNaN(value) || value === null || value === '') {
        throw new Error(`O campo ${fieldName} deve ser um número válido`);
    }
    return parseFloat(value);
}

async function showErrorResponse(response) {
    let message = `Erro na requisição: ${response.status} ${response.statusText}`;
    try {
        const errorData = await response.json();
        message = errorData.detail || errorData.message || errorData.error || message;
    } catch {
    }
    showAlert('danger', message);
}

function renderWinesTable(wines) {
    elements.winesTableBody.innerHTML = wines.length ? '' : `
        <tr><td colspan="5" class="text-center">Nenhum vinho encontrado</td></tr>
    `;

    wines.forEach(wine => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${wine.id}</td>
            <td>${wine.nome}</td>
            <td>${wine.documento}</td>
            <td>${wine.fornecedor}</td>
            <td><span class="badge ${wine.classificacao === 'BOM' ? 'bg-success' : 'bg-danger'}">${wine.classificacao}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary me-2 edit-btn" data-id="${wine.id}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${wine.id}">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        `;
        elements.winesTableBody.appendChild(row);
    });

    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', () => openEditModal(btn.dataset.id));
    });

    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', () => deleteWine(btn.dataset.id));
    });
}

function renderEditForm(wine) {
    elements.editModalBody.innerHTML = `
        <form id="editWineForm" class="row g-3">
            ${generateEditInput('Nome', 'editNome', wine.nome, 'text')}
            ${generateEditInput('Fornecedor', 'editFornecedor', wine.fornecedor, 'text')}
            <div class="col-md-6">
                <label for="editDocumento" class="form-label">Documento (não editável)</label>
                <input type="text" class="form-control" id="editDocumento" value="${wine.documento}" readonly>
            </div>
            ${generateEditInput('Acidez Fixa', 'editAcidezFixa', wine.acidez_fixa, 'number')}
            ${generateEditInput('Acidez Volátil', 'editAcidezVolatil', wine.acidez_volatil, 'number')}
            ${generateEditInput('Ácido Cítrico', 'editAcidoCitrico', wine.acido_citrico, 'number')}
            ${generateEditInput('Açúcar Residual', 'editAcucarResidual', wine.acucar_residual, 'number')}
            ${generateEditInput('Cloretos', 'editCloretos', wine.cloretos, 'number')}
            ${generateEditInput('SO₂ Livre', 'editDioxidoEnxofreLivre', wine.dioxido_enxofre_livre, 'number')}
            ${generateEditInput('SO₂ Total', 'editDioxidoEnxofreTotal', wine.dioxido_enxofre_total, 'number')}
            ${generateEditInput('Densidade', 'editDensidade', wine.densidade, 'number')}
            ${generateEditInput('pH', 'editPh', wine.ph, 'number')}
            ${generateEditInput('Sulfatos', 'editSulfatos', wine.sulfatos, 'number')}
            ${generateEditInput('Teor Alcoólico', 'editTeorAlcoolico', wine.teor_alcoolico, 'number')}
        </form>
    `;
}

function generateEditInput(label, id, value, type = 'text') {
    const step = type === 'number' ? 'step="any"' : '';
    return `
        <div class="col-md-${label.length > 12 ? '6' : '4'}">
            <label for="${id}" class="form-label">${label}</label>
            <input type="${type}" ${step} class="form-control" id="${id}" value="${value}" required>
        </div>
    `;
}

function showClassificationResult(classification) {
    elements.classificationResult.textContent = classification;
    elements.resultContainer.classList.remove('d-none');
    elements.resultContainer.scrollIntoView({ behavior: 'smooth' });
}

function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '1rem';
    alertDiv.style.left = '50%';
    alertDiv.style.transform = 'translateX(-50%)';
    alertDiv.style.zIndex = 1050;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.prepend(alertDiv);
    setTimeout(() => alertDiv.remove(), 7000);
}

function showLoading(show) {
    const loader = document.getElementById('loadingIndicator');
    if (loader) loader.style.display = show ? 'flex' : 'none';
}

function createLoader() {
    const loader = document.createElement('div');
    loader.id = 'loadingIndicator';
    loader.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.5); z-index: 9999; display: none;
        justify-content: center; align-items: center;
    `;
    loader.innerHTML = `
        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;">
            <span class="visually-hidden">Carregando...</span>
        </div>
    `;
    document.body.appendChild(loader);
}