document.addEventListener("DOMContentLoaded", function () {
    const userCountElement = document.getElementById('user-count-chart');
    const languageCountElement = document.getElementById('language-count-chart');
    // const locationCountElement = document.getElementById('location-count-chart');
    const genderCountElement = document.getElementById('gender-count-chart');
    const questionCountElement = document.getElementById('question-count-chart');
    const weeklyUserCountElement = document.getElementById('cumulative-user-count-chart');

    const userCountData = parseJSONSafe(userCountElement.dataset.chartData);
    const languageCountData = parseJSONSafe(languageCountElement.dataset.chartData);
    // const locationCountData = parseJSONSafe(locationCountElement.dataset.chartData);
    const genderCountData = parseJSONSafe(genderCountElement.dataset.chartData);
    const questionCountData = parseJSONSafe(questionCountElement.dataset.chartData);
    const weeklyUserCountData = parseJSONSafe(weeklyUserCountElement.dataset.chartData);

    const totalUsersElement = document.getElementById('total-users');
    const totalOnboardedUsersElement = document.getElementById('total-onboarded-users');
    const totalQuestionsElement = document.getElementById('total-question-count');

    const onboardedUserCountData = userCountElement.dataset.onboardedUserCount
        ? parseJSONSafe(userCountElement.dataset.onboardedUserCount)
        : {};

    const totalUsers = Object.values(userCountData).reduce((sum, count) => sum + count, 0);
    const totalOnboardedUsers = Object.values(onboardedUserCountData).reduce((sum, count) => sum + count, 0);
    const totalQuestions = Object.values(questionCountData).reduce((sum, count) => sum + count, 0);

    totalUsersElement.textContent = totalUsers;
    totalOnboardedUsersElement.textContent = totalOnboardedUsers;
    totalQuestionsElement.textContent = totalQuestions;

    createBarChart(userCountData, "user-count-chart");
    createCumulativeBarChart(weeklyUserCountData, onboardedUserCountData, "cumulative-user-count-chart", "Cumulative User Count");
    // createBarChart(locationCountData, "location-count-chart", "Location Count");
    createPieChart(questionCountData, "question-count-chart");
    createPieChart(languageCountData, "language-count-chart");
    createPieChart(genderCountData, "gender-count-chart");
    window.addEventListener('resize', () => {
        d3.selectAll('.chart-svg').remove();
        createBarChart(userCountData, "user-count-chart");
        createCumulativeBarChart(weeklyUserCountData, onboardedUserCountData, "cumulative-user-count-chart", "Cumulative User Count");
        createPieChart(questionCountData, "question-count-chart");
        createPieChart(languageCountData, "language-count-chart");
        createPieChart(genderCountData, "gender-count-chart");
    })
});

function parseJSONSafe(data) {
    try {
        return JSON.parse(data);
    } catch (e) {
        console.error('Invalid JSON data:', data);
        return {};
    }
}

// Function to create a bar chart
function createPieChart(data, elementId) {
    const chartContainer = d3.select(`#${elementId}`);
    const width = chartContainer.node().clientWidth;
    const height = Math.min(width, 350);
    const radius = Math.min(width, height) / 2;

    const svg = chartContainer.append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("class", "chart-svg")
        .append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`);

    const colorScale = d3.scaleOrdinal()
        .domain(Object.keys(d3.schemeCategory10))
        .range(["#ACCE27", "#F5547C", "#2D3FDD"]);

    const pie = d3.pie()
        .value(d => d[1]);

    const arc = d3.arc()
        .outerRadius(radius)
        .innerRadius(0);

    const labelArc = d3.arc()
        .outerRadius(radius - 42)
        .innerRadius(radius - 42);

    const dataReady = pie(Object.entries(data).filter(d => d[1] > 0));
    const total = d3.sum(dataReady, d => d.value);

    svg.selectAll("path")
        .data(dataReady)
        .enter().append("path")
        .attr("d", arc)
        .style("fill", d => colorScale(d.data[0]))

    const textFunction = elementId === 'question-count-chart'
        ? d => d.value
        : d => `${((d.value / total) * 100).toFixed(1)}%`;

    svg.selectAll("text")
        .data(dataReady)
        .enter().append("text")
        .attr("transform", d => `translate(${labelArc.centroid(d)})`)
        .attr("dy", "0.35em")
        .style("text-anchor", "middle")
        .style("fill", "#FFF")
        .text(textFunction); const legend = svg.append("g")

    const legendItems = legend.selectAll("g")
        .data(dataReady)
        .enter().append("g")
        .attr('transform', (d, i) => {
            const yPos = (i * 40) - (height / 2);
            return `translate(-${width / 2},${yPos})`;
        });

    legendItems.append("rect")
        .attr('x', 0)
        .attr("width", 18)
        .attr("height", 18)
        .attr("fill", d => colorScale(d.data[0]));

    legendItems.append("text")
        .attr("x", 25)
        .attr("y", 9)
        .attr("dy", "0.35em")
        .text(d => capitalizeFirstLetter(d.data[0]));
}

function createBarChart(data, elementId) {
    const chartContainer = d3.select(`#${elementId}`);
    const width = chartContainer.node().clientWidth || 400;
    const height = chartContainer.node().clientHeight || 300;
    const svg = chartContainer.append("svg")
        .attr("viewBox", `0 0 ${width} ${height}`)
        .attr("preserveAspectRatio", "xMidYMid meet")
        .attr("class", "chart-svg")

    const margin = { top: 40, right: 20, bottom: 60, left: 50 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const x = d3.scaleBand()
        .domain(Object.keys(data))
        .range([0, chartWidth])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([0, d3.max(Object.values(data))])
        .nice()
        .range([chartHeight, 0]);

    const chartArea = svg.append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    chartArea.append("g")
        .selectAll("rect")
        .data(Object.entries(data))
        .enter().append("rect")
        .attr("x", d => x(d[0]))
        .attr("y", d => y(d[1]))
        .attr("width", x.bandwidth())
        .attr("height", d => chartHeight - y(d[1]))
        .attr("fill", "steelblue");

    chartArea.append("g")
        .attr("transform", `translate(0, ${chartHeight})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("text-anchor", "end")
        .attr("dx", "-0.8em")
        .attr("dy", "0.18em")
        .attr("transform", "rotate(-50)")
        .attr('class', 'text-black');

    chartArea.select(".domain").attr("stroke", "black");
    chartArea.selectAll(".tick line").attr("stroke", "black");

    chartArea.append("g")
        .call(d3.axisLeft(y))
        .attr('class', 'text-black');

    chartArea.append("text")
        .attr("x", chartWidth / 2)
        .attr("y", -10)
        .attr("text-anchor", "middle")
        .style("font-size", "16px")

    chartArea.append("g")
        .selectAll("text")
        .data(Object.entries(data))
        .enter().append("text")
        .attr("x", d => x(d[0]) + x.bandwidth() / 2)
        .attr("y", d => y(d[1]) - 5)
        .attr("text-anchor", "middle")
        .style("font-size", "12px")
        .text(d => d[1]);
}

function createCumulativeBarChart(userData, onboardedUserData, elementId) {
    const chartContainer = d3.select(`#${elementId}`);
    const width = chartContainer.node().clientWidth || 400;
    const height = chartContainer.node().clientHeight || 300;

    const svg = chartContainer.append("svg")
        .attr("viewBox", `0 0 ${width} ${height}`)
        .attr("preserveAspectRatio", "xMidYMid meet")
        .attr("class", "chart-svg")

    const margin = { top: 40, right: 20, bottom: 40, left: 50 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const x = d3.scaleBand()
        .domain(Object.keys(userData))
        .range([0, chartWidth])
        .padding(0.1);

    const cumulativeUserData = Object.entries(userData).reduce((acc, [date, count], index) => {
        acc[date] = (index > 0 ? acc[Object.keys(acc)[index - 1]] : 0) + count;
        return acc;
    }, {});

    const cumulativeOnboardedUserData = Object.entries(onboardedUserData).reduce((acc, [date, count], index) => {
        acc[date] = (index > 0 ? acc[Object.keys(acc)[index - 1]] : 0) + count;
        return acc;
    }, {});

    const y = d3.scaleLinear()
        .domain([0, d3.max([...Object.values(cumulativeUserData), ...Object.values(cumulativeOnboardedUserData)])])
        .nice()
        .range([chartHeight, 0]);

    const chartArea = svg.append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    chartArea.append("g")
        .selectAll("rect")
        .data(Object.entries(cumulativeUserData))
        .enter().append("rect")
        .attr("x", d => x(d[0]))
        .attr("y", d => y(d[1]))
        .attr("width", x.bandwidth() / 2)
        .attr("height", d => chartHeight - y(d[1]))
        .attr("fill", "steelblue");

    chartArea.append("g")
        .selectAll("rect")
        .data(Object.entries(cumulativeOnboardedUserData))
        .enter().append("rect")
        .attr("x", d => x(d[0]) + x.bandwidth() / 2)
        .attr("y", d => y(d[1]))
        .attr("width", x.bandwidth() / 2)
        .attr("height", d => chartHeight - y(d[1]))
        .attr("fill", "orange")

    chartArea.append("g")
        .attr("transform", `translate(0, ${chartHeight})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("text-anchor", "middle")
        .attr('class', 'text-black');

    chartArea.select(".domain").attr("stroke", "black");
    chartArea.selectAll(".tick line").attr("stroke", "black");

    chartArea.append("g")
        .call(d3.axisLeft(y))
        .attr('class', 'text-black');

    chartArea.append("g")
        .selectAll("text")
        .data(Object.entries(cumulativeUserData))
        .enter().append("text")
        .attr("x", d => x(d[0]) + x.bandwidth() / 4)
        .attr("y", d => y(d[1]) - 5)
        .attr("text-anchor", "middle")
        .style("font-size", "12px")
        .text(d => d[1]);

    chartArea.append("g")
        .selectAll("text")
        .data(Object.entries(cumulativeOnboardedUserData))
        .enter().append("text")
        .attr("x", d => x(d[0]) + (3 * x.bandwidth()) / 4)
        .attr("y", d => y(d[1]) - 5)
        .attr("text-anchor", "middle")
        .style("font-size", "12px")
        .text(d => d[1]);
}
function capitalizeFirstLetter(text) {
    return text.replace(/\b\w/g, char => char.toUpperCase());
}