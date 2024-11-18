function showWidget(widgetId, content) {
  const widget = document.getElementById(widgetId);
  widget.textContent = content;
  widget.classList.add("visible");
}

function showSoccerWidget(widgetId, soccerData) {
  const soccerContainer = document.getElementById(widgetId);

  // Limpa o widget antes de adicionar novos jogos
  soccerContainer.innerHTML = "";

  soccerData.forEach((match) => {
    const matchItem = document.createElement("div");
    matchItem.classList.add("match-item");

    // Criar a descrição do jogo (rodada, times, placar, estádio, etc.)
    const matchInfoElement = document.createElement("p");
    matchInfoElement.textContent = `Round ${match.round} - ${match.tournament}`;

    const teamsElement = document.createElement("h3");
    teamsElement.textContent = `${match.homeTeam} vs ${match.visitingTeam}`;

    const scoreElement = document.createElement("p");
    scoreElement.textContent = `Score: ${match.score}`;

    const stadiumElement = document.createElement("p");
    stadiumElement.textContent = `Stadium: ${match.stadium}`;

    const dateElement = document.createElement("p");
    const matchDate = new Date(match.dataDaPartida).toLocaleString();
    dateElement.textContent = `Date: ${matchDate}`;

    // Adicionar todos os elementos criados no card de partida
    matchItem.appendChild(matchInfoElement);
    matchItem.appendChild(teamsElement);
    matchItem.appendChild(scoreElement);
    matchItem.appendChild(stadiumElement);
    matchItem.appendChild(dateElement);

    // Adicionar o item de partida ao container
    soccerContainer.appendChild(matchItem);
  });
}

function showNewsWidget(widgetId, newsData) {
  const newsContainer = document.getElementById(widgetId);

  // Limpa o widget antes de adicionar novas notícias
  newsContainer.innerHTML = "";

  newsData.forEach((news) => {
    const newsItem = document.createElement("div");
    newsItem.classList.add("news-item");

    const titleElement = document.createElement("h3");
    const titleLink = document.createElement("a");
    titleLink.href = news.url;
    titleLink.textContent = news.title;
    titleElement.appendChild(titleLink);

    const sourceAuthorElement = document.createElement("p");
    sourceAuthorElement.textContent = `Source: ${news.source}, Author: ${
      news.author || "Unknown"
    }`;

    const descriptionElement = document.createElement("p");
    descriptionElement.textContent = news.description;

    //    const imageElement = document.createElement("img");
    //    imageElement.src = news.urlToImage;
    //    imageElement.alt = news.title;
    //    imageElement.classList.add("news-image");

    const dateElement = document.createElement("p");
    const publishedDate = new Date(news.publishedAt).toLocaleString();
    dateElement.textContent = `Published at: ${publishedDate}`;

    //newsItem.appendChild(imageElement);
    newsItem.appendChild(titleElement);
    newsItem.appendChild(sourceAuthorElement);
    newsItem.appendChild(descriptionElement);
    newsItem.appendChild(dateElement);

    newsContainer.appendChild(newsItem);
  });
}

function showStockWidget(widgetId, stocksData) {
  const widget = document.getElementById(widgetId);
  if (!widget) return;

  let html = `
    <table border="1" cellpadding="10">
      <thead>
        <tr>
          <th>Symbol</th>
          <th>Name</th>
          <th>Price</th>
          <th>Change</th>
          <th>Change Percent</th>
          <th>Previous Close</th>
        </tr>
      </thead>
      <tbody>
  `;

  stocksData.forEach((stock) => {
    html += `
      <tr>
        <td>${stock.symbol}</td>
        <td>${stock.name}</td>
        <td>${stock.price.toFixed(2)}</td>
        <td style="color: ${stock.change >= 0 ? "green" : "red"};">
          ${stock.change.toFixed(2)}
        </td>
        <td>${stock.change_percent.toFixed(2)}%</td>
        <td>${stock.previous_close.toFixed(2)}</td>
      </tr>
    `;
  });

  html += `
      </tbody>
    </table>
  `;

  widget.innerHTML = html;
}

function hideWidget(widgetId) {
  const widget = document.getElementById(widgetId);
  widget.classList.remove("visible");
}

async function fetchHeaderData() {
  try {
    let temperature = await fetchTemperature();

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

    console.log(data);

    if (services.News) {
      showNewsWidget("news", services.News);
    } else {
      hideWidget("news");
    }

    if (services.Soccer) {
      showSoccerWidget("sports", services.Soccer);
    } else {
      hideWidget("sports");
    }

    if (services.B3) {
      showStockWidget("stocks", services.B3);
    } else {
      hideWidget("stocks");
    }

    if (services.Bible) {
      showWidget("verse", services.Bible.user_response);
    } else {
      hideWidget("verse");
    }
  } catch (error) {
    console.error("Error getting data from server:", error);
  }
}

window.onload = function () {
  fetchHeaderData();
  fetchWidgetsData();
};
