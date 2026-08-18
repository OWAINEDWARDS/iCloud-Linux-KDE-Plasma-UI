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
        spacing: Kirigami.Units.largeSpacing

        Layout.minimumWidth: 340
        Layout.preferredWidth: 400


        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.largeSpacing


            Kirigami.Icon {
                source: "folder-cloud"

                Layout.preferredWidth: Kirigami.Units.iconSizes.large
                Layout.preferredHeight: Kirigami.Units.iconSizes.large
            }


            ColumnLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing


                Kirigami.Heading {
                    text: "iCloud Linux"
                    level: 2
                }


                PlasmaComponents.Label {
                    text: backend.syncing ? "Synchronising with iCloud" : "iCloud sync service"
                    opacity: 0.7
                }
            }


            PlasmaComponents.Button {
                icon.name: "view-refresh"

                onClicked: backend.refresh()
            }
        }


        Kirigami.Separator {
            Layout.fillWidth: true
        }


        RowLayout {
            Layout.fillWidth: true


            PlasmaComponents.Label {
                text: "Service"
                Layout.fillWidth: true
            }


            Rectangle {
                width: 9
                height: 9
                radius: width / 2

                color: root.serviceColor()
            }


            PlasmaComponents.Label {
                text: backend.status
                color: root.serviceColor()
                font.bold: true
            }
        }


        RowLayout {
            Layout.fillWidth: true


            PlasmaComponents.Label {
                text: "Sync status"
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
            }
        }


        Controls.ProgressBar {
            Layout.fillWidth: true

            visible: backend.syncing
            indeterminate: true
        }


        ColumnLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing


            PlasmaComponents.Label {
                text: "Current file"
                font.bold: true
            }


            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 48

                radius: 8
                color: Kirigami.Theme.alternateBackgroundColor


                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Kirigami.Units.largeSpacing
                    anchors.rightMargin: Kirigami.Units.largeSpacing

                    spacing: Kirigami.Units.smallSpacing


                    Kirigami.Icon {
                        source: "text-x-generic"

                        Layout.preferredWidth: Kirigami.Units.iconSizes.small
                        Layout.preferredHeight: Kirigami.Units.iconSizes.small
                    }


                    PlasmaComponents.Label {
                        Layout.fillWidth: true

                        text: backend.currentFile !== "—" ? backend.currentFile : backend.syncing ? "Waiting for file activity..." : "No active file"
                        elide: Text.ElideMiddle
                    }
                }
            }
        }


        PlasmaComponents.Button {
            Layout.fillWidth: true
            Layout.preferredHeight: 40

            text: backend.syncing ? backend.syncPhase : "Sync Now"
            icon.name: "view-refresh"

            enabled: !backend.syncing && backend.status === "Running"

            onClicked: backend.sync()
        }


        Kirigami.Separator {
            Layout.fillWidth: true
        }


        RowLayout {
            Layout.fillWidth: true


            PlasmaComponents.Label {
                text: "Folders to sync"
                font.bold: true
                Layout.fillWidth: true
            }


            PlasmaComponents.Button {
                icon.name: "view-refresh"
                enabled: !backend.syncing

                onClicked: backend.refreshFolders()
            }
        }


        PlasmaComponents.Label {
            Layout.fillWidth: true

            visible: backend.rootFolders.length === 0
            text: "No iCloud root folders found yet. Run a sync or refresh the folder list."
            wrapMode: Text.WordWrap
            opacity: 0.7
        }


        Controls.ScrollView {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(folderColumn.implicitHeight, 200)

            visible: backend.rootFolders.length > 0
            clip: true


            ColumnLayout {
                id: folderColumn

                width: parent.width
                spacing: Kirigami.Units.smallSpacing


                Repeater {
                    model: backend.rootFolders


                    Controls.CheckBox {
                        Layout.fillWidth: true

                        text: modelData
                        checked: root.selectedFolders.indexOf(modelData) !== -1

                        enabled: !backend.syncing

                        onToggled: root.setFolderSelected(modelData, checked)
                    }
                }
            }
        }


        PlasmaComponents.Label {
            Layout.fillWidth: true

            visible: root.selectedFolders.length === 0 && backend.rootFolders.length > 0

            text: "At least one folder must be selected."
            color: Kirigami.Theme.negativeTextColor
        }


        PlasmaComponents.Button {
            Layout.fillWidth: true

            text: "Save & Apply"
            icon.name: "document-save"

            enabled: !backend.syncing && backend.rootFolders.length > 0 && root.selectedFolders.length > 0

            onClicked: backend.saveSyncFolders(root.selectedFolders)
        }


        PlasmaComponents.Label {
            Layout.fillWidth: true

            visible: backend.folderMessage !== ""

            text: backend.folderMessage
            wrapMode: Text.WordWrap

            color: backend.folderMessage.indexOf("ERROR:") === 0 ? Kirigami.Theme.negativeTextColor : Kirigami.Theme.positiveTextColor
        }


        Kirigami.Separator {
            Layout.fillWidth: true
        }


        PlasmaComponents.Label {
            text: "Service controls"
            font.bold: true
        }


        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing


            PlasmaComponents.Button {
                Layout.fillWidth: true

                text: "Start"
                icon.name: "media-playback-start"

                enabled: backend.status !== "Running" && backend.status !== "Starting..."

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