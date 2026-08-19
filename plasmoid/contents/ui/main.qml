import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls

import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

import org.icloudlinux.backend 1.0


PlasmoidItem {
    id: root

    Plasmoid.icon: "folder-cloud"

    property var selectedFolders: []

    readonly property int folderRowHeight: 34


    BackendBridge {
        id: backend
    }


    function serviceColor(){

        if (backend.status === "Running"){
            return Kirigami.Theme.positiveTextColor
        }

        if (backend.status === "Failed"){
            return Kirigami.Theme.negativeTextColor
        }

        return Kirigami.Theme.disabledTextColor
    }


    function loadFolderSelection(){

        var folders = []

        for (var i = 0; i < backend.syncFolders.length; i++){
            folders.push(backend.syncFolders[i])
        }

        root.selectedFolders = folders
    }


    function setFolderSelected(folderName, selected){

        var folders = root.selectedFolders.slice()
        var index = folders.indexOf(folderName)

        if (selected && index === -1){
            folders.push(folderName)
        }

        if (!selected && index !== -1){
            folders.splice(index, 1)
        }

        root.selectedFolders = folders
    }


    Connections {
        target: backend

        function onFoldersChanged(){
            root.loadFolderSelection()
        }
    }


    Component.onCompleted: {
        backend.refresh()
        root.loadFolderSelection()
    }


    fullRepresentation: ColumnLayout {
        spacing: Kirigami.Units.smallSpacing

        Layout.minimumWidth: 360
        Layout.preferredWidth: 390


        //
        // Header
        //

        RowLayout {
            Layout.fillWidth: true
            Layout.bottomMargin: Kirigami.Units.smallSpacing

            spacing: Kirigami.Units.largeSpacing


            Kirigami.Icon {
                source: "folder-cloud"

                Layout.preferredWidth: Kirigami.Units.iconSizes.large
                Layout.preferredHeight: Kirigami.Units.iconSizes.large
            }


            ColumnLayout {
                Layout.fillWidth: true

                spacing: 0


                Kirigami.Heading {
                    text: "iCloud Linux"
                    level: 2
                }


                PlasmaComponents.Label {
                    text: backend.syncing ? "Synchronising with iCloud" : "iCloud sync service"

                    opacity: 0.65
                }
            }


            PlasmaComponents.Button {
                icon.name: "view-refresh"

                onClicked: backend.refresh()
            }
        }


        //
        // Service
        //

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: serviceLayout.implicitHeight + Kirigami.Units.largeSpacing * 2

            radius: 8

            color: Kirigami.Theme.alternateBackgroundColor


            ColumnLayout {
                id: serviceLayout

                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter

                anchors.leftMargin: Kirigami.Units.largeSpacing
                anchors.rightMargin: Kirigami.Units.largeSpacing

                spacing: Kirigami.Units.smallSpacing


                RowLayout {
                    Layout.fillWidth: true


                    RowLayout {
                        Layout.fillWidth: true

                        spacing: Kirigami.Units.smallSpacing


                        Rectangle {
                            width: 9
                            height: 9

                            radius: width / 2

                            color: root.serviceColor()
                        }


                        PlasmaComponents.Label {
                            text: "Service"

                            font.bold: true
                        }
                    }


                    PlasmaComponents.Label {
                        text: backend.status

                        color: root.serviceColor()
                        font.bold: true
                    }
                }


                RowLayout {
                    Layout.fillWidth: true

                    spacing: Kirigami.Units.smallSpacing


                    PlasmaComponents.Button {
                        Layout.fillWidth: true

                        text: "Start"
                        icon.name: "media-playback-start"

                        enabled: backend.status !== "Running"
                                 && backend.status !== "Starting..."
                                 && backend.status !== "Stopping..."
                                 && backend.status !== "Restarting..."

                        onClicked: backend.startService()
                    }


                    PlasmaComponents.Button {
                        Layout.fillWidth: true

                        text: "Stop"
                        icon.name: "media-playback-stop"

                        enabled: backend.status === "Running"

                        onClicked: backend.stopService()
                    }


                    PlasmaComponents.Button {
                        Layout.fillWidth: true

                        text: "Restart"
                        icon.name: "view-refresh"

                        enabled: backend.status === "Running"

                        onClicked: backend.restartService()
                    }
                }
            }
        }


        Kirigami.Separator {
            Layout.fillWidth: true

            Layout.topMargin: Kirigami.Units.smallSpacing
            Layout.bottomMargin: Kirigami.Units.smallSpacing
        }


        //
        // Sync
        //

        RowLayout {
            Layout.fillWidth: true


            PlasmaComponents.Label {
                text: "Sync"

                font.bold: true

                Layout.fillWidth: true
            }


            PlasmaComponents.BusyIndicator {
                running: backend.syncing
                visible: backend.syncing

                Layout.preferredWidth: Kirigami.Units.iconSizes.small
                Layout.preferredHeight: Kirigami.Units.iconSizes.small
            }


            PlasmaComponents.Label {
                text: backend.syncing ? backend.syncPhase : "Idle"

                font.bold: backend.syncing
                opacity: backend.syncing ? 1.0 : 0.65
            }
        }


        Controls.ProgressBar {
            Layout.fillWidth: true

            visible: backend.syncing

            indeterminate: true
        }


        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: currentFileLayout.implicitHeight + Kirigami.Units.largeSpacing * 2

            radius: 8

            color: Kirigami.Theme.alternateBackgroundColor


            RowLayout {
                id: currentFileLayout

                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter

                anchors.leftMargin: Kirigami.Units.largeSpacing
                anchors.rightMargin: Kirigami.Units.largeSpacing

                spacing: Kirigami.Units.smallSpacing


                Kirigami.Icon {
                    source: "text-x-generic"

                    Layout.preferredWidth: Kirigami.Units.iconSizes.small
                    Layout.preferredHeight: Kirigami.Units.iconSizes.small
                }


                ColumnLayout {
                    Layout.fillWidth: true

                    spacing: 0


                    PlasmaComponents.Label {
                        text: "Current file"

                        font.bold: true
                        opacity: 0.6
                    }


                    PlasmaComponents.Label {
                        Layout.fillWidth: true

                        text: backend.currentFile !== "—"
                              ? backend.currentFile
                              : backend.syncing
                              ? "Waiting for file activity..."
                              : "No active file"

                        elide: Text.ElideMiddle
                    }
                }
            }
        }


        PlasmaComponents.Button {
            Layout.fillWidth: true
            Layout.preferredHeight: 38

            text: backend.syncing ? backend.syncPhase : "Sync Now"
            icon.name: "view-refresh"

            enabled: !backend.syncing && backend.status === "Running"

            onClicked: backend.sync()
        }


        Kirigami.Separator {
            Layout.fillWidth: true

            Layout.topMargin: Kirigami.Units.smallSpacing
            Layout.bottomMargin: Kirigami.Units.smallSpacing
        }


        //
        // Folder selection
        //

        ColumnLayout {
            Layout.fillWidth: true

            spacing: 0


            PlasmaComponents.Label {
                text: "Folders to sync"

                font.bold: true
            }


            PlasmaComponents.Label {
                text: {
                    if (backend.rootFolders.length === 0){
                        return "Waiting for iCloud folder list"
                    }

                    if (backend.rootFolders.length > 3){
                        return backend.rootFolders.length + " folders available • scroll list for more"
                    }

                    return backend.rootFolders.length + " folders available"
                }

                opacity: 0.6
            }
        }


        PlasmaComponents.Label {
            Layout.fillWidth: true

            visible: backend.rootFolders.length === 0

            text: "Run a sync to discover the folders in your iCloud root."

            wrapMode: Text.WordWrap
            opacity: 0.65
        }


        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: backend.rootFolders.length === 0 ? 0 : Math.min(backend.rootFolders.length, 3) * root.folderRowHeight + 8

            visible: backend.rootFolders.length > 0

            radius: 8

            color: Kirigami.Theme.alternateBackgroundColor


            ListView {
                id: folderList

                anchors.fill: parent
                anchors.margins: 4

                clip: true

                model: backend.rootFolders

                boundsBehavior: Flickable.StopAtBounds
                snapMode: ListView.SnapOneItem

                maximumFlickVelocity: 300
                flickDeceleration: 7500

                pixelAligned: true

                interactive: contentHeight > height


                delegate: Item {
                    width: folderList.width
                    height: root.folderRowHeight


                    Controls.CheckBox {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter

                        anchors.leftMargin: Kirigami.Units.smallSpacing
                        anchors.rightMargin: Kirigami.Units.smallSpacing

                        text: modelData

                        checked: root.selectedFolders.indexOf(modelData) !== -1

                        enabled: !backend.syncing

                        onToggled: root.setFolderSelected(modelData, checked)
                    }
                }
            }


            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom

                height: 1

                visible: folderList.contentY + folderList.height < folderList.contentHeight - 1

                color: Kirigami.Theme.disabledTextColor
                opacity: 0.25
            }
        }


        RowLayout {
            Layout.fillWidth: true

            visible: backend.rootFolders.length > 0

            spacing: Kirigami.Units.smallSpacing


            PlasmaComponents.Label {
                Layout.fillWidth: true

                text: root.selectedFolders.length === 0
                      ? "Select at least one folder"
                      : root.selectedFolders.length + " selected"

                color: root.selectedFolders.length === 0
                       ? Kirigami.Theme.negativeTextColor
                       : Kirigami.Theme.textColor

                opacity: root.selectedFolders.length === 0 ? 1.0 : 0.6
            }


            PlasmaComponents.Button {
                text: "Save & Apply"
                icon.name: "document-save"

                enabled: !backend.syncing && root.selectedFolders.length > 0

                onClicked: backend.saveSyncFolders(root.selectedFolders)
            }
        }


        PlasmaComponents.Label {
            Layout.fillWidth: true

            visible: backend.folderMessage !== ""

            text: backend.folderMessage

            wrapMode: Text.WordWrap

            color: backend.folderMessage.indexOf("ERROR:") === 0
                   ? Kirigami.Theme.negativeTextColor
                   : Kirigami.Theme.positiveTextColor
        }
    }
}