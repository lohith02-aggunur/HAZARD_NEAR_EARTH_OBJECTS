document.addEventListener("DOMContentLoaded", function () {
    const rawData = JSON.parse(document.getElementById("neoData").textContent);

    let hazardous = 0, safe = 0;
    let diameters = [], velocities = [], missDistances = [];

    rawData.forEach(d => {
        const dia = parseFloat(d.diameter_min);
        const vel = parseFloat(d.relative_velocity);
        const miss = parseFloat(d.miss_distance);
        const isHaz = d.hazardous === "True";

        if (isHaz) hazardous++;
        else safe++;

        diameters.push(dia);
        velocities.push(vel);
        missDistances.push(miss);
    });

    Plotly.newPlot('hazardPie', [{
        values: [hazardous, safe],
        labels: ['Hazardous', 'Not Hazardous'],
        type: 'pie'
    }], { title: 'Hazard Distribution' });

    Plotly.newPlot('diameterHist', [{
        x: diameters,
        type: 'histogram',
        marker: { color: 'skyblue' }
    }], { title: 'Diameter Distribution (Min)', xaxis: { title: 'Diameter (km)' } });

    Plotly.newPlot('missScatter', [{
        x: missDistances,
        y: velocities,
        mode: 'markers',
        type: 'scatter',
        marker: { color: 'orange' }
    }], {
        title: 'Miss Distance vs Velocity',
        xaxis: { title: 'Miss Distance (AU)' },
        yaxis: { title: 'Velocity (km/s)' }
    });
});
