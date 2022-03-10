var id = null;
function myMove1() {

    var container = document.getElementById("ChildHolder");
    var lines = document.querySelectorAll('.transaction-line>line');

    var consumers = document.getElementsByClassName('consumer');

    for (let i in lines) {
        // consumer = consumers[i];
        // consumerRect = getXY(consumer);
        line = lines[i];
        line.x1.baseVal.valueAsString;
        line.x1.baseVal.value;
        clearInterval(id);
        id = setInterval(frame, 10);
        function frame() {
            linePoints = getPointsOnSVGLine(line);
            // https://www.gowtham.design/blog/svg-path-commands-drawing-straight-lines
            if (pos == Math.min(Math.max(100, container.style.width - elem.style.width), 350)) {
                clearInterval(id);
            } else {
                pos++;
                elem.style.top = pos + 'px';
                elem.style.left = pos + 'px';
            }
        }
    }
}

function getPointsOnSVGLine(svgLineNode, gap = 1) {
    function getValue(p) {
        return p.baseVal.value;
    }
    x1 = getValue(line.x1);
    y1 = getValue(line.y1);
    x2 = getValue(line.x2);
    y2 = getValue(line.y2);

    return getPointsOnLine(x1, y1, x2, y2, gap);
}

function myMove1() {
    var elem = document.getElementById("myAnimation");
    var container = document.getElementById("centreWidgetContainer");

    elem.innerText = container.style.width - elem.style.width
    var pos = 0;
    clearInterval(id);
    id = setInterval(frame, 10);
    function frame() {
        if (pos == Math.min(Math.max(100, container.style.width - elem.style.width), 350)) {
            clearInterval(id);
        } else {
            pos++;
            elem.style.top = pos + 'px';
            elem.style.left = pos + 'px';
        }
    }
}

function drawCoordinates(ctx, point) {
    var pointSize = 3; // Change according to the size of the point.
    // var ctx = document.getElementById("canvas").getContext("2d");


    ctx.fillStyle = "#ff2626"; // Red color
    x = point[0]
    y = point[1]
    ctx.beginPath(); //Start path
    ctx.arc(x, y, pointSize, 0, Math.PI * 2, true); // Draw a point using the arc function of the canvas with a point structure.
    ctx.fill(); // Close the path and fill.
}

function drawCanvas() {
    var canvas = document.getElementById('myCanvas');
    var context = canvas.getContext('2d');
    var centerX = canvas.width / 2;
    var centerY = canvas.height;
    var radius = (canvas.width / 2.0) * 0.667;

    context.beginPath();
    context.scale(1, 0.5);
    context.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
    context.fillStyle = 'green';
    context.fill();
    context.lineWidth = 5;
    context.strokeStyle = '#003300';
    context.stroke();
}

function getPointsEllipse(centerX, centerY, radius, numberOfPoints = 4.0, scaleX = 1.0, scaleY = 1.0) {
    function x(a) {
        return centerX + (radius * scaleX) * Math.cos(Math.PI * 2.0 * a)
    }
    function y(a) {
        return centerY + (radius * scaleY) * Math.sin(Math.PI * 2.0 * a)
    }

    points = []
    for (i = 0; i < numberOfPoints; i++) {
        points[i] = [x((i) / numberOfPoints), y((i) / numberOfPoints)]
    }
    return points;
}

function drawPoints(context, centerX, centerY, radius, numberOfPoints = 4.0, scaleX = 1.0, scaleY = 1.0) {
    points = getPointsEllipse(centerX, centerY, radius, numberOfPoints, scaleX, scaleY)
    console.log(points);
    for (let i in points) {
        point = points[i];
        console.log(point);
        drawCoordinates(context, point)
    }
}

function getPointsPercentages(numberOfPoints, childRadius) {
    points = []
    for (let i in [...Array(numberOfPoints).keys()]) {
        // Get the direction of the consumer from center 
        // where
        //  - (1*Math.PI)/4 == point vertically above centre.
        //  - (2*Math.PI)/4 == point top right.
        //  - (3*Math.PI)/4 == point middle right -> (100%W - 0.5cons.W%, 50%H - 0.5cons.H%).
        //  - (4*Math.PI)/4 == point bottom right -> (100%W - 0.5cons.W%, 100%H - 0.5cons.H%).

        // start with (<X> * Math.PI)/4
        childRadius = Math.max(Math.min(1, childRadius), 0);
        numberOfPoints = Math.max(1, numberOfPoints)
        divisor = numberOfPoints / 2.0
        X = i / divisor
        // XRad = (i * Math.Pi) / divisor  // 0.25Pi [0,2Pi]
        // pointCart = [Math.cos(XRad), Math.sin(XRad)]
        // points.push(pointCart);
        // point = [pointCart[0], pointCart[1] * -1 + 1]
        // X = XRad
        // X /= 2 * Math.PI // 0.25 in [0,1]
        X *= 4.0 // 1 in [0,4]
        var point = null

        if (0 <= X && X < 1) {
            point = [1 * (1 - childRadius), (0.5 * (1 - childRadius)) - (X * 0.5)]
        } else if (X < 2) {
            X = X - 1.0
            point = [(1 * (1 - childRadius)) - (X * 0.5), 0]
        } else if (X < 3) {
            X = X - 2.0
            point = [(0.5 * (1 - childRadius)) - (X * 0.5), 0]
        } else if (X < 4) {
            X = X - 3.0
            point = [0, 0 + (X * 0.5)]
        } else if (X < 5) {
            X = X - 4.0
            point = [0, (0.5 * (1 - childRadius)) + (X * 0.5)]
        } else if (X < 6) {
            X = X - 5.0
            point = [0 + (X * 0.5), 1 * (1 - childRadius)]
        } else if (X < 7) {
            X = X - 6.0
            point = [(0.5 * (1 - childRadius)) + (X * 0.5), 1 * (1 - childRadius)]
        } else if (X < 8) {
            X = X - 7.0
            point = [1 * (1 - childRadius), (1 * (1 - childRadius)) - (X * 0.5)]
        }
        points.push(point);
    }
    return points;
}

function getPointsOnLine(x1, y1, x2, y2, gap = 1) {
    m = (y2 - y1) / (x2 - x1);
    c = y1 - (m * x1);

    dist = (((y2 - y1) ** 2.0) + ((x2 - x1) ** 2.0)) ** 0.5;
    x3 = x1 + gap;
    y3 = y1 + (gap * m);
    dist_per_unit = (((y3 - y1) ** 2.0) + ((x3 - x1) ** 2.0)) ** 0.5;
    N = dist / dist_per_unit;
    points = [];
    for (i = 0; i < N; i += gap) {
        points.push([x1 + (i * gap), y1 + (i * m * gap)]);
    }
    return points;
}

function getPointsOnLineInContainer(containerElem, x1_pcnt, x2_pcnt, y1_pcnt, y2_pcnt, gap = 1) {
    rect = getXY(containerElem);

    x1 = rect.left + (rect.width * x1_pcnt)
    x2 = rect.left + (rect.top * x2_pcnt)
    y1 = rect.left + (rect.width * y1_pcnt)
    y2 = rect.left + (rect.top * y2_pcnt)

    return getPointsOnLine(x1, y1, x2, y2, gap);
}

function getXY(containerElem) {
    rect = containerElem.getBoundingClientRect();
    scrollLeft = window.pageXOffset || document.documentElement.scrollLeft,
        scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    return {
        top: rect.top + scrollTop,
        left: rect.left + scrollLeft,
        width: rect.width,
        height: rect.height,
        rect: rect
    };
}

function drawSpiderChildren(elem, numChildren, childRadius = 0.05) {

    // var context = elem.getContext('2d');
    var centerX = elem.width / 2;
    var centerY = elem.height / 2;
    // var radius = (Math.min(elem.width, elem.height) / 2.0);

    points = getPointsPercentages(numChildren, childRadius);
    money_d = 10;
    rad = money_d / 2;
    divs = points.map(function (p, i) {
        return `<svg class="transaction-line" 
                    width="100%" height="100%" 
                    viewBox="0 0 100 100"
                    preserveAspectRatio="none meet"
                    style="position: absolute; 
                    left:0%; top:0%; 
            ">` +
            '<path d=" M ' + ((p[0] + childRadius * 0.5) * 100.0) +
            ',' + ((p[1] + childRadius * 0.5) * 100.0) +
            ' l ' + (50.0 - ((p[0] + childRadius * 0.5) * 100.0)) + ',' + (50.0 - ((p[1] + childRadius * 0.5) * 100.0)) + '"' +
            ' stroke="white" stroke-width="0.5" fill="none"/>' +
            `<circle r="1" 
                cx="`+ ((p[0] + childRadius * 0.5) * 100.0) + `" 
                cy="`+ ((p[1] + childRadius * 0.5) * 100.0) + `" 
                id="dot`+ i + `" 
                style="fill: pink;">
                <animateTransform attributeName="transform" 
                    type="translate" 
                    from="0 0" 
                    to="` + (50.0 - ((p[0] + childRadius * 0.5) * 100.0)) + ' ' + (50.0 - ((p[1] + childRadius * 0.5) * 100.0)) + `" 
                    begin="0s" 
                    dur="5s" 
                    repeatCount="indefinite">
                </animateTransform>
            </circle>
            <image width="`+ money_d + `" height="` + money_d + `"
                xlink:href="assets/noun-money-1636594.svg">
                <animateTransform
                                attributeName="transform"
                                type="translate"
                                from="`+ ((p[0] + childRadius * 0.5) * 100.0 - rad) + ' ' + ((p[1] + childRadius * 0.5) * 100.0 - rad) + `" 
                                to="`+ (50 - rad) + ` ` + (50 - rad) +`" 
                                begin="0s" 
                                dur="5s" 
                                repeatCount="indefinite">
                </animateTransform>
            </image>
        </svg>` +
            '<div class="consumer" style="position: absolute; left: ' +
            (p[0] * 100) + '%; top: ' + (p[1] * 100) + '%">' +
            (i + 1) + '</div>';
        return '<svg class="transaction-line" width="100%" height="100%" style="position: absolute; left:0%; top:0%; ">' +
            '<line id="line' + i + '"' +
            ' x1="' + ((p[0] + childRadius * 0.5) * 100.0) +
            '%" y1="' + ((p[1] + childRadius * 0.5) * 100.0) +
            '%" x2="' + "50%" +
            '" y2="' + "50%" +
            '" stroke="black"/>' +
            `<circle
                r="2"
                cx="` + ((p[0] + childRadius * 0.5) * 100.0) + `%"
                cy="` + ((p[1] + childRadius * 0.5) * 100.0) + `%"
                id="dot`+ i + `"
                style="fill: #dd1819">` +
            `<animateTransform
                    attributeName="transform"
                    type="translate"
                    from="` + ((p[0] + childRadius * 0.5) * 100.0) + `% ` + ((p[1] + childRadius * 0.5) * 100.0) + `%"
                    to="50% 50%"
                    begin="0s"
                    dur="2s"
                    repeatCount="Indefinite" />` +
            `</circle>` +
            '</svg>' +
            '<div class="consumer" style="position: absolute; left: ' +
            (p[0] * 100) + '%; top: ' + (p[1] * 100) + '%">' +
            (i + 1) + '</div>';
    });
    return divs;
    //TODO P1: Use CSS Media Queries on the class name to create the ViewPort of the SVG to be the same aspect ratio to the aspect ratio (height / width of its container)
}

const dot = {
    sprite: null,
    track: null,

    // Initialize the dot: connect sprite and track properties with supplied SVG elements
    init: function (sprite, track) {
        this.sprite = document.getElementById(sprite);
        this.track = document.getElementById(track);
    },

    // Put the dot on its spot
    move: function (u) {
        const p = this.track.getPointAtLength(u * this.track.getTotalLength());
        this.sprite.setAttribute("transform", `translate(${p.x}, ${p.y})`);
    }
};

const anim = {
    start: function (duration) {
        this.duration = duration;
        this.tZero = Date.now();

        requestAnimationFrame(() => this.run());
    },

    run: function () {

        let u = Math.min((Date.now() - this.tZero) / this.duration, 1);

        if (u < 1) {
            // Keep requesting frames, till animation is ready
            requestAnimationFrame(() => this.run());
        } else {
            this.onFinish();
        }

        dot.move(u);
    },

    onFinish: function () {
        // Schedule the animation to restart
        setTimeout(() => this.start(this.duration), 1000);
    }
};

window.onload = () => {

    var container = document.getElementById("ChildHolder");
    divs = drawSpiderChildren(container, 16, 0.05);
    console.log(divs);
    container.innerHTML = divs.join('');

    //TODO: Load the javascript of the customers and pull them all in.
    // Parse the information and populate the correct number of parameters.
    // then look at bootstrap or something to show tooltips for the customer / entity information.
    // Do we need to strart considering how we could potentially use flutter as the front end instead before going further down this road.?

    // dot.init('dot1', 'line1');
    // anim.start(2000);
}

