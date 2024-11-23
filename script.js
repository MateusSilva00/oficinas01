function openPopup(content) {
  if (content === "stocks") {
    displayStockData();
  }

  if (content === "bible") {
    displayBibleQuote();
  }

  if (content === "news") {
    displayNews();
  }

  if (content === "soccer") {
    displaySoccer();
  }

  document.getElementById("popup").classList.add("active");
}

function closePopup() {
  document.getElementById("popup").classList.remove("active");
}

async function fetchHeaderData() {
  try {
    // let temperature = await fetchTemperature();
    let temperature = 24;

    const date = new Date();
    let day = date.getDate();
    let month = date.getMonth() + 1;
    let year = date.getFullYear();
    let currentDate = `${day}/${month}/${year}`;

    document.getElementById("date").textContent = currentDate;
    document.getElementById("temperature").textContent = `${temperature}°C`;

    updateClock();
    setInterval(updateClock, 1000);
  } catch (error) {
    console.error("Error getting data from server:", error);
  }
}

async function fetchTemperature() {
  const url = "https://open-weather13.p.rapidapi.com/city/curitiba/PT_BR";
  const options = {
    method: "GET",
    headers: {
      "x-rapidapi-key": "0a9281447bmsh050ae130452ed49p1bc1cdjsn28d1e7d60a18",
      "x-rapidapi-host": "open-weather13.p.rapidapi.com",
    },
  };

  try {
    const response = await fetch(url, options);
    const result = await response.json();

    let tempFahrenheit = result.main.temp;

    let tempCelsius = ((tempFahrenheit - 32) * 5) / 9;
    tempCelsius = tempCelsius.toFixed(2);

    console.log(`Temperatura em Celsius: ${tempCelsius}°C`);

    return tempCelsius;
  } catch (error) {
    console.error(error);
  }
}

function updateClock() {
  const now = new Date();
  let hours = now.getHours().toString().padStart(2, "0");
  let minutes = now.getMinutes().toString().padStart(2, "0");
  let seconds = now.getSeconds().toString().padStart(2, "0");
  let currentTime = `${hours}:${minutes}:${seconds}`;

  document.getElementById("time").textContent = currentTime;
}

async function fetchWidgetsData() {
  try {
    const response = await fetch("http://127.0.0.1:8000/users/1", {
      headers: {
        accept: "application/json",
      },
    });

    if (!response.ok) throw new Error("Error on the API response");

    const data = await response.json();
    let services = data.services;

    document.getElementById("greeting").textContent = `Olá, ${data.username}`;

    window.stockData = services.B3;
    window.bibleQuote = services.Bible;
    window.newsData = services.News;
    window.soccerData = services.Soccer;
  } catch (error) {
    console.error("Error getting data from server:", error);
  }
}

function displayStockData() {
  const popupText = document.getElementById("popup-text");
  popupText.innerHTML = "";

  console.log(window.stockData);

  if (window.stockData && window.stockData.length > 0) {
    console.log(window.stockData);
    const table = document.createElement("table");
    table.classList.add("stock-table");

    const headers = [
      "Ação",
      "Código",
      "Valor (R$)",
      "Variação no Dia (%)",
      "Volume",
      "Última Atualização",
    ];
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    headers.forEach((header) => {
      const th = document.createElement("th");
      th.textContent = header;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    window.stockData.forEach((stock) => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${stock.StockName}</td>
        <td>${stock.StockCode}</td>
        <td>${stock.ValueFormatted}</td>
        <td>${stock.ChangeDayFormatted || "N/A"}</td>
        <td>${stock.VolumeFormatted}</td>
        <td>${new Date(stock.Date).toLocaleString()}</td>
      `;

      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    popupText.appendChild(table);
  } else {
    popupText.innerText = "Nenhuma ação disponível.";
  }
}

function displayBibleQuote() {
  const popupText = document.getElementById("popup-text");
  popupText.innerHTML = "";

  if (window.bibleQuote != null) {
    const verseContainer = document.createElement("div");
    verseContainer.classList.add("verse-container");

    const quote = document.createElement("blockquote");
    quote.textContent = `"${window.bibleQuote.quote}"`;
    verseContainer.appendChild(quote);

    const book = document.createElement("p");
    book.classList.add("bible-book");
    book.textContent = `— ${window.bibleQuote.book}`;
    verseContainer.appendChild(book);

    const interpretation = document.createElement("p");
    interpretation.classList.add("bible-interpretation");
    interpretation.textContent = window.bibleQuote.interpretation;
    verseContainer.appendChild(interpretation);

    // Adiciona o conteúdo no popup
    popupText.appendChild(verseContainer);
  } else {
    popupText.innerText = "Nenhuma citação bíblica disponível.";
  }
}

function displayNews() {
  const popupText = document.getElementById("popup-text");
  popupText.innerHTML = "";

  if (window.newsData && window.newsData.length > 0) {
    window.newsData.forEach((newsItem) => {
      const newsContainer = document.createElement("div");
      newsContainer.classList.add("news-container");

      const newsTitle = document.createElement("h3");
      newsTitle.classList.add("news-title");
      newsTitle.innerHTML = `<a target="_blank">${newsItem.title}</a>`;
      newsContainer.appendChild(newsTitle);

      const newsSource = document.createElement("p");
      newsSource.classList.add("news-source");
      newsSource.innerHTML = `Fonte: ${newsItem.source}`;
      newsContainer.appendChild(newsSource);

      const newsDescription = document.createElement("p");
      newsDescription.classList.add("news-description");
      newsDescription.innerText = newsItem.description;
      newsContainer.appendChild(newsDescription);

      const newsDate = document.createElement("p");
      newsDate.classList.add("news-date");
      newsDate.innerText = `Publicado em: ${new Date(
        newsItem.publishedAt
      ).toLocaleString()}`;
      newsContainer.appendChild(newsDate);

      const newsImage = document.createElement("img");
      newsImage.classList.add("news-image");
      newsImage.src = newsItem.urlToImage;
      newsContainer.appendChild(newsImage);

      popupText.appendChild(newsContainer);
    });
  } else {
    popupText.innerText = "Nenhuma notícia disponível.";
  }
}

function displaySoccer() {
  const popupText = document.getElementById("popup-text");
  popupText.innerHTML = ""; // Limpa o conteúdo do popup

  if (window.soccerData && window.soccerData.length > 0) {
    const container = document.createElement("div");
    container.classList.add("soccer-table-container");

    // Título da tabela
    const title = document.createElement("div");
    title.classList.add("soccer-table-title");
    title.textContent = "Partidas do Dia";

    // Tabela de partidas
    const table = document.createElement("table");
    table.classList.add("soccer-table");

    const headers = [
      "Rodada",
      // "Status da Partida",
      "Data",
      "Campeonato",
      "Time da Casa",
      "Time Visitante",
      "Estádio",
      "Placar",
    ];
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    headers.forEach((header) => {
      const th = document.createElement("th");
      th.textContent = header;
      th.classList.add("header");
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    window.soccerData.forEach((match) => {
      const row = document.createElement("tr");

      // <td>${match.matchStatus === "10" ? "Em andamento" : "Finalizado"}</td>
      row.innerHTML = `
        <td>${match.round}</td>
        <td>${new Date(match.dataDaPartida).toLocaleString()}</td>
        <td>${match.tournament}</td>
        <td>${match.homeTeam}</td>
        <td>${match.visitingTeam}</td>
        <td>${match.stadium}</td>
        <td>${match.score}</td>
      `;

      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    container.appendChild(title);
    container.appendChild(table);

    popupText.appendChild(container);
  } else {
    popupText.innerText = "Nenhuma partida disponível.";
  }
}

function initializeZoey() {
  // Selecionando os elementos da interface
  const zoeyToggle = document.getElementById("zoey-toggle");
  const zoeyPopup = document.getElementById("zoey-popup");
  const startRecordingBtn = document.getElementById("start-recording");

  let isRecording = false;
  let mediaRecorder;
  let audioChunks = [];

  // Abrir ou fechar o popup quando o ícone "Zoey" for clicado
  zoeyToggle.addEventListener("click", () => {
    zoeyPopup.style.display =
      zoeyPopup.style.display === "block" ? "none" : "block";
  });

  // Controlar a gravação com o botão
  startRecordingBtn.addEventListener("click", () => {
    if (isRecording) {
      // Se já estiver gravando, parar a gravação
      mediaRecorder.stop(); // Isso vai chamar a função onstop automaticamente

      startRecordingBtn.disabled = true;
      startRecordingBtn.textContent = "Finalizando...";

      // Fechar o popup após a gravação, quando a gravação estiver finalizada
      setTimeout(() => {
        zoeyPopup.style.display = "none"; // Esconde o popup após a gravação
        alert("Gravação finalizada. Enviando para a Zoey!");
        startRecordingBtn.disabled = false;
        startRecordingBtn.textContent = "Iniciar Gravação"; // Restaura o texto do botão
        isRecording = false; // Atualiza o estado da gravação
      }, 1000); // Espera 1 segundo para finalizar a gravação
    } else {
      // Se não estiver gravando, iniciar a gravação
      startRecordingBtn.disabled = true;
      startRecordingBtn.textContent = "Gravando...";

      // Acessar o microfone e iniciar a gravação
      navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then((stream) => {
          mediaRecorder = new MediaRecorder(stream);

          mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
          };

          mediaRecorder.onstop = () => {
            // Aqui será processado o áudio após a gravação ser parada
            const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioChunks = []; // Limpar os chunks para a próxima gravação
          };

          mediaRecorder.start(); // Inicia a gravação
          isRecording = true; // Marca que está gravando

          startRecordingBtn.textContent = "Parar Gravação"; // Altera o texto do botão
        })
        .catch((error) => {
          alert("Erro ao acessar o microfone: " + error.message);
        });
    }
  });
}

window.onload = function () {
  fetchHeaderData();
  fetchWidgetsData();
  initializeZoey();
};
