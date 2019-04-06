let searchBar = document.getElementById("searchBar");
let pathBar = document.getElementById("pathBar");
let scroll_id = null;
let docCount = 0;
let searchQueued = false;
let coolingDown = false;
let selectedDirs = [];

function toggleSearchBar() {
    searchQueued = true;
}

let tree = new InspireTree({
    selection: {
        mode: 'checkbox'
    },
    data: mimeMap
});
new InspireTreeDOM(tree, {
    target: '.tree'
});

//Select all
tree.select();
tree.node("any").deselect();

tree.on("node.click", function(event, node, handler) {
    event.preventTreeDefault();

    if (node.id === "any") {

        if (!node.itree.state.checked) {
            tree.deselect();
        }
    } else {
        tree.node("any").deselect();
    }

    handler();
    searchQueued = true;
});

new autoComplete({
    selector: '#pathBar',
    minChars: 1,
    delay: 75,
    renderItem: function (item){
        return '<div class="autocomplete-suggestion" data-val="' + item + '">' + item + '</div>';
    },
    source: async function(term, suggest) {
        term = term.toLowerCase();

        const choices = await getPathChoices();

        let matches = [];
        for (let i=0; i<choices.length; i++) {
            if (~choices[i].toLowerCase().indexOf(term)) {
                matches.push(choices[i]);
            }
        }
        suggest(matches);
    },
    onSelect: function() {
        searchQueued = true;
    }
});

function makeStatsCard(searchResult) {

    let statsCard = document.createElement("div");
    statsCard.setAttribute("class", "card");
    let statsCardBody = document.createElement("div");
    statsCardBody.setAttribute("class", "card-body");

    let stat = document.createElement("p");
    stat.appendChild(document.createTextNode(searchResult["hits"]["total"] + " results in " + searchResult["took"] + "ms"));

    let sizeStat = document.createElement("span");
    sizeStat.appendChild(document.createTextNode(humanFileSize(searchResult["aggregations"]["total_size"]["value"])));

    statsCardBody.appendChild(stat);
    statsCardBody.appendChild(sizeStat);
    statsCard.appendChild(statsCardBody);

    return statsCard;
}

function makeResultContainer() {
    let resultContainer = document.createElement("div");
    resultContainer.setAttribute("class", "card-columns");

    return resultContainer;
}

/**
 * https://stackoverflow.com/questions/10420352
 */
function humanFileSize(bytes) {

    if(bytes === 0) {
        return "? B"
    }

    let thresh = 1000;
    if(Math.abs(bytes) < thresh) {
        return bytes + ' B';
    }
    let units = ['kB','MB','GB','TB','PB','EB','ZB','YB'];
    let u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while(Math.abs(bytes) >= thresh && u < units.length - 1);

    return bytes.toFixed(1) + ' ' + units[u];
}

/**
 * https://stackoverflow.com/questions/6312993
 */
function humanTime (sec_num) {
    sec_num = Math.floor(sec_num);
    let hours   = Math.floor(sec_num / 3600);
    let minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    let seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0" + hours;}
    if (minutes < 10) {minutes = "0" + minutes;}
    if (seconds < 10) {seconds = "0" + seconds;}
    return hours + ":" + minutes + ":" + seconds;
}


function initPopover() {
    $('[data-toggle="popover"]').popover({
        trigger: "focus",
        delay: { "show": 0, "hide": 100 },
        placement: "bottom",
        html: true
    });
}

/**
 * Enable gif loading on hover
 * @param thumbnail
 * @param documentId
 */
function gifOver(thumbnail, documentId) {
    let callee = arguments.callee;

    thumbnail.addEventListener("mouseover", function () {

        thumbnail.mouseStayedOver = true;

        window.setTimeout(function() {
            if (thumbnail.mouseStayedOver) {
                thumbnail.removeEventListener('mouseover', callee, false);

                //Load gif
                thumbnail.setAttribute("src", "/file/" + documentId);
            }
        }, 750);

    });

    thumbnail.addEventListener("mouseout", function() {
        //Reset timer
        thumbnail.mouseStayedOver = false;
        thumbnail.setAttribute("src", "/thumb/" + documentId);

    })
}

function downloadPopover(element, documentId) {
    element.setAttribute("data-content",
        '<a class="btn btn-sm btn-primary" href="/dl/'+ documentId +'"><i class="fas fa-download"></i> Download</a>' +
        '<a class="btn btn-sm btn-success" style="margin-left:3px;" href="/file/'+ documentId + '" target="_blank"><i class="fas fa-eye"></i> View</a>');
    element.setAttribute("data-toggle", "popover");
    element.addEventListener("mouseover", function() {
        element.focus();
    });
}

/**
 *
 * @param hit
 * @returns {Element}
 */
function createDocCard(hit) {

    let docCard = document.createElement("div");
    docCard.setAttribute("class", "card");
    docCard.setAttribute("tabindex", "-1");

    let docCardBody = document.createElement("div");
    docCardBody.setAttribute("class", "card-body document");

    let link = document.createElement("a");
    link.setAttribute("href", "/document/" + hit["_id"]);
    link.setAttribute("target", "_blank");

    //Title
    let title = document.createElement("p");
    title.setAttribute("class", "file-title");
    let extension = hit["_source"].hasOwnProperty("extension") && hit["_source"]["extension"] !== "" ? "." + hit["_source"]["extension"] : "";

    if (hit.hasOwnProperty("highlight") && hit["highlight"].hasOwnProperty("name")) {
        title.insertAdjacentHTML('afterbegin', hit["highlight"]["name"] + extension);
    } else if (hit.hasOwnProperty("highlight") && hit["highlight"].hasOwnProperty("name.nGram")) {
        title.insertAdjacentHTML('afterbegin', hit["highlight"]["name.nGram"] + extension);
    } else {
        title.appendChild(document.createTextNode(hit["_source"]["name"] + extension));
    }

    title.setAttribute("title", hit["_source"]["path"] + "/" + hit["_source"]["name"] + extension);
    docCard.appendChild(title);

    let tagContainer = document.createElement("div");
    tagContainer.setAttribute("class", "card-text");

    if (hit["_source"].hasOwnProperty("mime") && hit["_source"]["mime"] !== null) {

        let tags = [];
        let thumbnail = null;
        let thumbnailOverlay = null;
        let imgWrapper = document.createElement("div");
        imgWrapper.setAttribute("style", "position: relative");

        let mimeCategory = hit["_source"]["mime"].split("/")[0];

        //Thumbnail
        switch (mimeCategory) {

            case "video":
                thumbnail = document.createElement("video");
                let vidSource = document.createElement("source");
                vidSource.setAttribute("src", "/file/" + hit["_id"]);
                vidSource.setAttribute("type", "video/webm");
                thumbnail.appendChild(vidSource);
                thumbnail.setAttribute("class", "fit");
                thumbnail.setAttribute("loop", "");
                thumbnail.setAttribute("controls", "");
                thumbnail.setAttribute("preload", "none");
                thumbnail.setAttribute("poster", "/thumb/" + hit["_id"]);
                thumbnail.addEventListener("dblclick", function() {
                    thumbnail.webkitRequestFullScreen();
                });

                break;
            case "image":
                thumbnail = document.createElement("img");
                thumbnail.setAttribute("class", "card-img-top fit");
                thumbnail.setAttribute("src", "/thumb/" + hit["_id"]);
                break;
        }

        //Thumbnail overlay
        switch (mimeCategory) {

            case "image":
                thumbnailOverlay = document.createElement("div");
                thumbnailOverlay.setAttribute("class", "card-img-overlay");

                //Resolution
                let resolutionBadge = document.createElement("span");
                resolutionBadge.setAttribute("class", "badge badge-resolution");
                if (hit["_source"].hasOwnProperty("width")) {
                    resolutionBadge.appendChild(document.createTextNode(hit["_source"]["width"] + "x" + hit["_source"]["height"]));
                }
                thumbnailOverlay.appendChild(resolutionBadge);

                var format = hit["_source"]["format_name"];

                //Hover
                if(format === "GIF") {
                    gifOver(thumbnail, hit["_id"]);
                }
                break;

            case "video":
                //Duration
                if (hit["_source"].hasOwnProperty("duration")) {
                    thumbnailOverlay = document.createElement("div");
                    thumbnailOverlay.setAttribute("class", "card-img-overlay");
                    let durationBadge = document.createElement("span");
                    durationBadge.setAttribute("class", "badge badge-resolution");
                    durationBadge.appendChild(document.createTextNode(humanTime(hit["_source"]["duration"])));
                    thumbnailOverlay.appendChild(durationBadge);
                }
        }

        //Tags
        switch (mimeCategory) {

            case "video":
                if (hit["_source"].hasOwnProperty("format_long_name")) {
                    let formatTag = document.createElement("span");
                    formatTag.setAttribute("class", "badge badge-pill badge-video");
                    formatTag.appendChild(document.createTextNode(hit["_source"]["format_long_name"].replace(" ", "")));
                    tags.push(formatTag);
                }

                break;
            case "image": {
                let formatTag = document.createElement("span");
                formatTag.setAttribute("class", "badge badge-pill badge-image");
                formatTag.appendChild(document.createTextNode(format));
                tags.push(formatTag);
            }
                break;
            case "audio": {
                if (hit["_source"].hasOwnProperty("format_long_name")) {
                    let formatTag = document.createElement("span");
                    formatTag.setAttribute("class", "badge badge-pill badge-audio");
                    formatTag.appendChild(document.createTextNode(hit["_source"]["format_long_name"]));
                    tags.push(formatTag);
                }

            }

                break;
            case "text": {
                let formatTag = document.createElement("span");
                formatTag.setAttribute("class", "badge badge-pill badge-text");
                formatTag.appendChild(document.createTextNode(hit["_source"]["encoding"]));
                tags.push(formatTag);
            }

                break;
        }

        //Content
        if (hit.hasOwnProperty("highlight") && hit["highlight"].hasOwnProperty("content")) {

            let contentDiv = document.createElement("div");
            contentDiv.setAttribute("class", "content-div bg-light");
            contentDiv.insertAdjacentHTML('afterbegin', hit["highlight"]["content"][0]);
            docCard.appendChild(contentDiv);
        }

        //Audio
        if (mimeCategory === "audio" && hit["_source"].hasOwnProperty("format_long_name")) {

            let audio = document.createElement("audio");
            audio.setAttribute("preload", "none");
            audio.setAttribute("class", "audio-fit fit");
            audio.setAttribute("controls", "");
            audio.setAttribute("type", hit["_source"]["mime"]);
            audio.setAttribute("src", "file/" + hit["_id"]);

            docCard.appendChild(audio)
        }

        if (thumbnail !== null) {
            imgWrapper.appendChild(thumbnail);
            docCard.appendChild(imgWrapper);
        }
        if (thumbnailOverlay !== null) {
            imgWrapper.appendChild(thumbnailOverlay);
        }

        for (let i = 0; i < tags.length; i++) {
            tagContainer.appendChild(tags[i]);
        }


    }

    //Size tag
    let sizeTag = document.createElement("small");
    sizeTag.appendChild(document.createTextNode(humanFileSize(hit["_source"]["size"])));
    sizeTag.setAttribute("class", "text-muted");
    tagContainer.appendChild(sizeTag);


    //Download button
    downloadPopover(docCard, hit["_id"]);

    docCardBody.appendChild(link);
    docCard.appendChild(docCardBody);

    link.appendChild(title);
    docCardBody.appendChild(tagContainer);

    return docCard;
}

function makePageIndicator(searchResult) {
    let pageIndicator = document.createElement("div");
    pageIndicator.appendChild(document.createTextNode(docCount + " / " +searchResult["hits"]["total"]));
    return pageIndicator;
}


function insertHits(resultContainer, hits) {
    for (let i = 0 ; i < hits.length; i++) {
        resultContainer.appendChild(createDocCard(hits[i]));
        docCount++;
    }
}

window.addEventListener("scroll", function () {

    if (!coolingDown) {

        let threshold = 350;

        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - threshold) {
            //load next page

            let xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function() {
                if (this.readyState === 4 && this.status === 200) {

                    let searchResult = JSON.parse(this.responseText);
                    let searchResults = document.getElementById("searchResults");
                    let hits = searchResult["hits"]["hits"];

                    //Page indicator
                    let pageIndicator = makePageIndicator(searchResult);
                    searchResults.appendChild(pageIndicator);

                    //Result container
                    let resultContainer = makeResultContainer();
                    searchResults.appendChild(resultContainer);

                    insertHits(resultContainer, hits);

                    initPopover();

                    if (hits.length !== 0) {
                        coolingDown = false;
                    }
                } else if (this.status === 500) {
                    window.location.reload()
                }
            };
            xhttp.open("GET", "/scroll?scroll_id=" + scroll_id, true);
            xhttp.send();
            coolingDown = true;
        }
    }
});

function getSelectedMimeTypes() {
    let mimeTypes = [];

    let selected = tree.selected();

    for (let i = 0; i < selected.length; i++) {

        if(selected[i].id === "any") {
            return "any"
        }

        //Only get children
        if (selected[i].text.indexOf("(") !== -1) {
            mimeTypes.push(selected[i].id);
        }
    }

    return mimeTypes
}

function search() {

    if (searchQueued === true) {
        searchQueued = false;

        //Clear old search results
        let searchResults =  document.getElementById("searchResults");
        while (searchResults.firstChild) {
            searchResults.removeChild(searchResults.firstChild);
        }

        let query = searchBar.value;

        let xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState === 4 && this.status === 200) {

                let searchResult = JSON.parse(this.responseText);
                scroll_id = searchResult["_scroll_id"];

                //Search stats
                searchResults.appendChild(makeStatsCard(searchResult));

                //Autocomplete
                if (searchResult.hasOwnProperty("suggest") && searchResult["suggest"].hasOwnProperty("path")) {
                    pathAutoComplete = [];
                    for (let i = 0; i < searchResult["suggest"]["path"][0]["options"].length; i++) {
                        pathAutoComplete.push(searchResult["suggest"]["path"][0]["options"][i].text)
                    }
                }

                //Setup page
                let resultContainer = makeResultContainer();
                searchResults.appendChild(resultContainer);

                //Insert search results (hits)
                docCount = 0;
                insertHits(resultContainer, searchResult["hits"]["hits"]);

                //Initialise download/view button popover
                initPopover();
            }
        };

        xhttp.open("POST", "/search", true);

        let postBody = {};
        postBody.q = query;
        postBody.size_min = size_min;
        postBody.size_max = size_max;
        postBody.mime_types = getSelectedMimeTypes();
        postBody.must_match = document.getElementById("barToggle").checked;
        postBody.directories = selectedDirs;
        postBody.path = pathBar.value.replace(/\/$/, "").toLowerCase(); //remove trailing slashes
        xhttp.setRequestHeader('content-type', 'application/json');
        xhttp.send(JSON.stringify(postBody));
    }
}

let pathAutoComplete = [];
let size_min = 0;
let size_max = 10000000000000;

searchBar.addEventListener("keyup", function () {
    searchQueued = true;
});

//Size slider
$("#sizeSlider").ionRangeSlider({
    type: "double",
    grid: false,
    force_edges: true,
    min: 0,
    max: 3684.03149864,
    from: 0,
    to: 3684.03149864,
    min_interval: 5,
    drag_interval: true,
    prettify: function (num) {

        if(num === 0) {
            return "0 B"
        } else if (num >= 3684) {
            return humanFileSize(num * num * num) + "+";
        }

        return humanFileSize(num * num * num)
    },
    onChange: function(e) {
        size_min = (e.from * e.from * e.from);
        size_max = (e.to * e.to * e.to);

        if (e.to >=  3684) {
            size_max = 10000000000000;
        }

        searchQueued = true;
    }
});

//Directories select
function updateDirectories() {
    let selected = $('#directories').find('option:selected');
    selectedDirs = [];
    $(selected).each(function(){
        selectedDirs.push(parseInt($(this).val()));
    });

    searchQueued = true;
}
document.getElementById("directories").addEventListener("change", updateDirectories);
updateDirectories();
searchQueued = false;

//Suggest
function getPathChoices() {
    return new Promise(getPaths => {

        let xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState === 4 && this.status === 200) {
                getPaths(JSON.parse(xhttp.responseText))
            }
        };
        xhttp.open("GET", "/suggest?prefix=" + pathBar.value, true);
        xhttp.send();
    });
}

document.getElementById("pathBar").addEventListener("keyup", function () {
    searchQueued = true;
});

window.setInterval(search, 300);