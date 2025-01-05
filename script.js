let priceChart = null; // 用于存储图表对象

document.getElementById("search-btn").addEventListener("click", function () {
  const origin = document.getElementById("departure").value;
  const destination = document.getElementById("destination").value;
  const flydate = document.getElementById("date").value;

  if (!origin || !destination) {
    alert("请填写完整的起点和终点信息！");
    return;
  }

  // 使用 fetch 请求后端 API 获取历史价格数据
  fetch(
    `http://127.0.0.1:5000/api/flight-prices?origin=${origin}&destination=${destination}&flydate=${flydate}`
  )
    .then((response) => response.json())
    .then((data) => {
      console.log("Received data:", data); // 调试输出
      if (data.error) {
        alert(data.error);
        return;
      }

      // 取得历史价格数据
      const historicalDates = data.dates.map((date) => {
        // 转换日期格式为 YYYY-MM-DD
        const dateObj = new Date(date);
        return dateObj.toISOString().split("T")[0]; // 格式化为 "YYYY-MM-DD"
      });

      // 转换价格为数字
      const historicalPrices = data.prices.map((price) => parseFloat(price));

      // 检查数据是否为空
      if (historicalDates.length === 0 || historicalPrices.length === 0) {
        alert("没有找到历史价格数据！");
        return;
      }

      // 更新航班信息部分（如果需要）
      const resultsDiv = document.getElementById("results");
      resultsDiv.innerHTML = `查询成功，历史价格数据已加载<br>`;

      // 如果图表已存在，则更新图表数据
      if (priceChart) {
        priceChart.data.labels = historicalDates; // 更新日期数据
        priceChart.data.datasets[0].data = historicalPrices; // 更新价格数据
        priceChart.update(); // 更新图表
      } else {
        // 如果图表不存在，则创建新的图表
        const ctx = document.getElementById("priceChart").getContext("2d");
        priceChart = new Chart(ctx, {
          type: "line",
          data: {
            labels: historicalDates, // 历史日期
            datasets: [
              {
                label: "历史价格波动",
                data: historicalPrices, // 历史价格
                borderColor: "rgba(75, 192, 192, 1)",
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderWidth: 2,
                fill: true,
              },
            ],
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: false,
                title: {
                  display: true,
                  text: "价格 (¥)",
                },
              },
              x: {
                title: {
                  display: true,
                  text: "日期",
                },
              },
            },
          },
        });
      }
    })
    .catch((error) => {
      console.error("Error fetching flight data:", error);
      alert("无法获取数据，请稍后再试。");
    });
});
