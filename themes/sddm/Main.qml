import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    width: Screen.width
    height: Screen.height
    color: "#0a0a0a"

    Connections {
        target: sddm
        function onLoginFailed() { errorMsg.visible = true }
    }

    Canvas {
        id: infinityCanvas
        width: 400
        height: 200
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -120

        onPaint: {
            var ctx = getContext("2d");
            var cx = width / 2;
            var cy = height / 2;
            var r = 55;
            ctx.beginPath();
            for (var i = 0; i <= 1000; i++) {
                var t = (i / 1000) * 2 * Math.PI;
                var x = cx + (r * 2.0 * Math.cos(t)) / (1 + Math.sin(t) * Math.sin(t));
                var y = cy + (r * 1.9 * Math.sin(t) * Math.cos(t)) / (1 + Math.sin(t) * Math.sin(t));
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }
            ctx.strokeStyle = "#e8e8e8";
            ctx.lineWidth = 5;
            ctx.stroke();
            [[cx, cy],[cx+26,cy],[cx-26,cy]].forEach(function(d) {
                ctx.beginPath();
                ctx.arc(d[0], d[1], 5, 0, 2 * Math.PI);
                ctx.fillStyle = "#e8272a";
                ctx.fill();
            });
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: -30
        text: "CENTRAL"
        color: "#e8e8e8"
        font.pixelSize: 22
        font.letterSpacing: 14
        font.weight: Font.Light
    }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 100
        spacing: 12

        TextField {
            id: userField
            width: 280
            placeholderText: "username"
            color: "#e8e8e8"
            placeholderTextColor: "#555555"
            background: Rectangle {
                color: "#1a1a1a"
                border.color: "#333333"
                border.width: 1
                radius: 4
            }
            padding: 12
            font.pixelSize: 14
        }

        TextField {
            id: passField
            width: 280
            placeholderText: "password"
            echoMode: TextInput.Password
            color: "#e8e8e8"
            placeholderTextColor: "#555555"
            background: Rectangle {
                color: "#1a1a1a"
                border.color: "#333333"
                border.width: 1
                radius: 4
            }
            padding: 12
            font.pixelSize: 14
            onTextChanged: errorMsg.visible = false
            Keys.onReturnPressed: sddm.login(userField.text, passField.text, 2)
        }

        Text {
            id: errorMsg
            visible: false
            width: 280
            text: "incorrect password"
            color: "#e8272a"
            font.pixelSize: 13
            font.letterSpacing: 1
            horizontalAlignment: Text.AlignHCenter
        }

        Rectangle {
            width: 280
            height: 42
            color: "#e8272a"
            radius: 4

            Text {
                anchors.centerIn: parent
                text: "sign in"
                color: "#ffffff"
                font.pixelSize: 14
                font.letterSpacing: 2
            }

            MouseArea {
                anchors.fill: parent
                onClicked: sddm.login(userField.text, passField.text, 2)
            }
        }
    }
}
