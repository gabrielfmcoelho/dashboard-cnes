window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        get_width: function (value) {
            console.log("get_width...");
            if (window.innerWidth >= 758) {
                return "grande";
            }
            else {
                return "pequeno";
            }
        }
    }
});