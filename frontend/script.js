

// Dados para o gráfico
let dadosGrafico = {
    labels: [],
    temp: [],
    umid: [],
    luz: [],
    faces: []
};

// Cria o gráfico
const ctx = document.getElementById('grafico').getContext('2d');
const grafico = new Chart(ctx, {
    type: 'line',
    data: {
        labels: dadosGrafico.labels,
        datasets: [
            {
                label: 'Temperatura (°C)',
                data: dadosGrafico.temp,
                borderColor: '#ff6384',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.4
            },
            {
                label: 'Umidade (%)',
                data: dadosGrafico.umid,
                borderColor: '#36a2eb',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.4
            },
            {
                label: 'Luminosidade / 10',
                data: dadosGrafico.luz,
                borderColor: '#ffce56',
                backgroundColor: 'rgba(255, 206, 86, 0.1)',
                tension: 0.4
            },
            {
                label: 'Rostos Detectados',
                data: dadosGrafico.faces,
                borderColor: '#9966ff',
                backgroundColor: 'rgba(153, 102, 255, 0.1)',
                tension: 0.4
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Busca dados da API
async function buscarDados() {
    try {
        // Busca leituras
        const respLeituras = await fetch(`${API_URL}/leituras?limite=1`);
        const dataLeituras = await respLeituras.json();
        
        if (dataLeituras.leituras && dataLeituras.leituras.length > 0) {
            const ultima = dataLeituras.leituras[dataLeituras.leituras.length - 1];
            atualizarCards(ultima);
            atualizarGrafico(ultima);
        }
        
        // Busca thresholds
        const respThresholds = await fetch(`${API_URL}/thresholds`);
        const thresholds = await respThresholds.json();
        atualizarInputsThresholds(thresholds);
        
        document.getElementById('ultima-atualizacao').textContent = 
            new Date().toLocaleTimeString('pt-BR');
        
    } catch (erro) {
        console.error('Erro ao buscar dados:', erro);
    }
}

// Atualiza os cards com as leituras
function atualizarCards(leitura) {
    // Temperatura
    document.getElementById('temp').textContent = leitura.temperatura.toFixed(1);
    const tempMax = parseFloat(document.getElementById('temp-max').value);
    atualizarStatus('temp', leitura.temperatura > tempMax, 'Boa');
    
    // Umidade
    document.getElementById('umid').textContent = leitura.umidade.toFixed(1);
    const umidMin = parseFloat(document.getElementById('umid-min').value);
    atualizarStatus('umid', leitura.umidade < umidMin, 'Boa');
    
    // Luminosidade
    document.getElementById('luz').textContent = leitura.luminosidade; // Sempre mostra valor
    const luzMin = parseInt(document.getElementById('luz-min').value);
    atualizarStatus('luz', leitura.luminosidade < luzMin, 'Boa');
    
    // LED
    const ledLigado = leitura.led_ativo;
    document.getElementById('led-texto').textContent = ledLigado ? 'Ligado' : 'Desligado';
    const ledIndicator = document.getElementById('led-indicator');
    ledIndicator.className = `led-indicator ${ledLigado ? 'led-on' : 'led-off'}`;

    // Faces
    if (leitura.hasOwnProperty('faces_detectadas')) {
        document.getElementById('faces').textContent = leitura.faces_detectadas;
        atualizarStatus('faces', leitura.faces_detectadas > 0, 'Nenhum');
    }
}

// Atualiza status visual
function atualizarStatus(tipo, alerta, textoNormal = 'Normal') {
    const elemento = document.getElementById(`${tipo}-status`);
    if (alerta) {
        elemento.className = 'status alerta';
        elemento.textContent = 'Alerta';
    } else {
        elemento.className = 'status normal';
        elemento.textContent = textoNormal;  // 'Boa' quando dentro do limite
    }
}

// Atualiza gráfico
function atualizarGrafico(leitura) {
    const agora = new Date().toLocaleTimeString('pt-BR');
    
    dadosGrafico.labels.push(agora);
    dadosGrafico.temp.push(leitura.temperatura);
    dadosGrafico.umid.push(leitura.umidade);
    dadosGrafico.luz.push(leitura.luminosidade / 10);  // Divide para escala
    if (leitura.hasOwnProperty('faces_detectadas')) {
        dadosGrafico.faces.push(leitura.faces_detectadas);
    } else {
        dadosGrafico.faces.push(0);
    }
    
    // Limita a 20 pontos
    if (dadosGrafico.labels.length > 20) {
        dadosGrafico.labels.shift();
        dadosGrafico.temp.shift();
        dadosGrafico.umid.shift();
        dadosGrafico.luz.shift();
        dadosGrafico.faces.shift();
    }
    
    grafico.update();
}

// Atualiza inputs de thresholds
function atualizarInputsThresholds(thresholds) {
    document.getElementById('temp-max').value = thresholds.temp_max;
    document.getElementById('umid-min').value = thresholds.umid_min;
    document.getElementById('luz-min').value = thresholds.luz_min;
}

// Envia novos thresholds para API
async function atualizarThresholds() {
    const thresholds = {
        temp_max: parseFloat(document.getElementById('temp-max').value),
        umid_min: parseFloat(document.getElementById('umid-min').value),
        luz_min: parseInt(document.getElementById('luz-min').value)
    };
    
    try {
        const resposta = await fetch(`${API_URL}/thresholds`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(thresholds)
        });
        
        if (resposta.ok) {
            alert('✅ Limites atualizados com sucesso!');
        } else {
            alert('❌ Erro ao atualizar limites');
        }
    } catch (erro) {
        console.error('Erro:', erro);
        alert('❌ Erro de conexão com a API');
    }
}

// Atualiza automaticamente a cada 3 segundos
setInterval(buscarDados, 3000);

// Busca inicial
buscarDados();
