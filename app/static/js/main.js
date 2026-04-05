(function () {
    const engineSelect = document.getElementById('engine');
    const yearSelect = document.getElementById('model_year');
    const validYearsMap = window.polestarValidYears || {};

    function rebuildYears() {
        if (!engineSelect || !yearSelect) return;
        const selectedEngine = engineSelect.value;
        const currentYear = yearSelect.value;
        const allowedYears = validYearsMap[selectedEngine] || ['2014', '2015', '2016', '2017', '2018'];

        const firstOption = '<option value="">Select year</option>';
        yearSelect.innerHTML = firstOption + allowedYears.map(function (year) {
            const selected = currentYear === year ? ' selected' : '';
            return '<option value="' + year + '"' + selected + '>' + year + '</option>';
        }).join('');

        if (currentYear && !allowedYears.includes(currentYear)) {
            yearSelect.value = '';
        }
    }

    if (engineSelect && yearSelect) {
        engineSelect.addEventListener('change', rebuildYears);
        rebuildYears();
    }
})();
