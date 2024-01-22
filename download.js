javascript: (function () {
    var data = {
    };
    function q(selector) {
        try {
            return document.querySelector(selector).textContent;
        } catch (error) {
            return "";
        }
    }
    data["id"] = q("#gallery_id").split('#')[1];
    title = {}; subtitle = {};
    title["before"] = q("h1.title span.before");
    title["pretty"] = q("h1.title span.pretty");
    title["after"] = q("h1.title span.after");
    subtitle["before"] = q("h2.title span.before");
    subtitle["pretty"] = q("h2.title span.pretty");
    subtitle["after"] = q("h2.title span.after");
    data["title"] = title;
    data["subtitle"] = subtitle;

    parodies = []; tags = []; artists = []; groups = []; characters = []; languages = []; categories = [];
    pages = 0; uploaded = "";
    tagElements = document.querySelectorAll("span.tags a");
    tagElements.forEach(element => {
        s = element.querySelector("span.name").textContent;
        if(element.href.includes("/tag/")) tags.push(s);
        else if(element.href.includes("/parody/")) parodies.push(s);
        else if(element.href.includes("/artist/")) artists.push(s);
        else if(element.href.includes("/group/")) groups.push(s);
        else if(element.href.includes("/character/")) characters.push(s);
        else if(element.href.includes("/language/")) languages.push(s);
        else if(element.href.includes("/category/")) categories.push(s);
        else if(element.href.includes("?q=pages")) pages = parseInt(s);
    });
    uploaded = document.querySelector("time.nobold").title;
    data["tags"] = tags;
    data["parodies"] = parodies;
    data["artists"] = artists;
    data["groups"] = groups;
    data["characters"] = characters;
    data["languages"] = languages;
    data["categories"] = categories;
    data["pages"] = pages;
    data["uploaded"] = uploaded;

    imgs = [];
    imgElements = document.querySelectorAll("div.thumb-container img");
    imgElements.forEach(element => {
        if(element.src.startsWith("https://"))
            imgs.push(element.src);
    });
    data["imgs"] = imgs;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://localhost:8901", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(data));
})();