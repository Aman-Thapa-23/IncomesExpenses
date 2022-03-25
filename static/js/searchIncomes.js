const searchField = document.querySelector("#SearchField");
const appTable = document.querySelector(".app-table");
const tableOutput = document.querySelector(".table-output");
const tableOutputBody = document.querySelector(".table-output-body");
const paginationContainer = document.querySelector(".pagination-container");
const noResults = document.querySelector(".no-results");

tableOutput.style.display = "none";

searchField.addEventListener("keyup", SearchValue);

function SearchValue(event) {
  const searchVal = event.target.value;

  if (searchVal.trim().length > 0) {
    paginationContainer.style.display = "none";

    tableOutputBody.innerHTML = "";

    fetch("/income/search-incomes", {
      body: JSON.stringify({ searchText: searchVal }),
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("data", data);
        appTable.style.display = "none";
        tableOutput.style.display = "block";

        if (data.length === 0) {
          noResults.style.display = "block";
          tableOutput.style.display = "none";
        } else {
          noResults.style.display = "none";
          data.forEach((item) => {
            tableOutputBody.innerHTML += `
                  <tr>
                    <td>${item.amount}</td>
                    <td>${item.source}</td>
                    <td>${item.description}</td>
                    <td>${item.date}</td>
                  </tr>
                  `;
          });
        }
      });
  } else {
    tableOutput.style.display = "none";
    appTable.style.display = "block";
    paginationContainer.style.display = "block";
  }
}
