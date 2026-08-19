#include "backend_bridge.h"

#include <QDBusConnection>
#include <QDBusMessage>
#include <QDBusPendingCall>
#include <QDBusPendingCallWatcher>
#include <QDBusPendingReply>
#include <QDebug>

namespace{
    const QString SERVICE_NAME = QStringLiteral("org.iCloudLinux");
    const QString OBJECT_PATH = QStringLiteral("/Backend");
    const QString INTERFACE_NAME = QStringLiteral("org.iCloudLinux.Backend");
}

BackendBridge::BackendBridge(QObject *parent) : QObject(parent){
    QDBusConnection bus = QDBusConnection::sessionBus();

    bool state_connected = bus.connect(SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME, QStringLiteral("state_changed"), QStringLiteral("sbss"), this, SLOT(onStateChanged(QString,bool,QString,QString)));

    if (!state_connected){
        qWarning() << "Could not connect to state_changed D-Bus signal";
    }

    bool folders_connected = bus.connect(SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME, QStringLiteral("folders_changed"), QStringLiteral("asas"), this, SLOT(onFoldersChanged(QStringList,QStringList)));

    if (!folders_connected){
        qWarning() << "Could not connect to folders_changed D-Bus signal";
    }

    refresh();
}

QString BackendBridge::status() const{
    return m_status;
}

bool BackendBridge::syncing() const{
    return m_syncing;
}

QString BackendBridge::currentFile() const{
    return m_currentFile;
}

QString BackendBridge::syncPhase() const{
    return m_syncPhase;
}

QStringList BackendBridge::rootFolders() const{
    return m_rootFolders;
}

QStringList BackendBridge::syncFolders() const{
    return m_syncFolders;
}

QString BackendBridge::folderMessage() const{
    return m_folderMessage;
}

void BackendBridge::refresh(){
    requestStatus();
    requestSyncing();
    requestCurrentFile();
    requestSyncPhase();

    refreshFolders();
}

void BackendBridge::refreshFolders(){
    requestRootFolders();
    requestSyncFolders();
}


void BackendBridge::startService(){
    callMethod(QStringLiteral("Start"));
}

void BackendBridge::stopService(){
    callMethod(QStringLiteral("Stop"));
}

void BackendBridge::restartService(){
    callMethod(QStringLiteral("Restart"));
}

void BackendBridge::sync(){
    callMethod(QStringLiteral("Sync"));
}

void BackendBridge::onStateChanged(const QString &status, bool syncing, const QString &currentFile, const QString &syncPhase){
    bool changed = m_status != status || m_syncing != syncing || m_currentFile != currentFile || m_syncPhase != syncPhase;

    m_status = status;
    m_syncing = syncing;
    m_currentFile = currentFile;
    m_syncPhase = syncPhase;

    if (changed){
        emit stateChanged();
    }
}

void BackendBridge::onFoldersChanged(const QStringList &rootFolders, const QStringList &syncFolders){
    m_rootFolders = rootFolders;
    m_syncFolders = syncFolders;

    emit foldersChanged();
}

void BackendBridge::requestStatus(){

    QDBusMessage message = QDBusMessage::createMethodCall(SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME, QStringLiteral("GetStatus"));
    QDBusPendingCall pending_call = QDBusConnection::sessionBus().asyncCall(message);
    QDBusPendingCallWatcher *watcher = new QDBusPendingCallWatcher(pending_call, this);
    QObject::connect(watcher, &QDBusPendingCallWatcher::finished, this, [this](QDBusPendingCallWatcher *call){
        QDBusPendingReply<QString> reply = *call;

        if (reply.isError()){
            qWarning() << "GetStatus D-Bus call failed:" << reply.error().message();

            call->deleteLater();
            return;
        }

        QString new_status = reply.value();

        if (m_status != new_status){
            m_status = new_status;

            emit stateChanged();
        }

        call->deleteLater();
    });
}

void BackendBridge::requestSyncing(){

    QDBusMessage message = QDBusMessage::createMethodCall(SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME, QStringLiteral("IsSyncing"));
    QDBusPendingCall pending_call = QDBusConnection::sessionBus().asyncCall(message);
    QDBusPendingCallWatcher *watcher = new QDBusPendingCallWatcher(pending_call, this);

    QObject::connect(watcher, &QDBusPendingCallWatcher::finished, this, [this](QDBusPendingCallWatcher *call){
        QDBusPendingReply<bool> reply = *call;

        if (reply.isError()){
            qWarning() << "IsSyncing D-Bus call failed:" << reply.error().message();

            call->deleteLater();
            return;
        }

        bool new_syncing = reply.value();

        if (m_syncing != new_syncing){
            m_syncing = new_syncing;

            emit stateChanged();
        }

        call->deleteLater();
    });
}

void BackendBridge::requestCurrentFile(){

    QDBusMessage message = QDBusMessage::createMethodCall(SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME, QStringLiteral("GetCurrentFile"));
    QDBusPendingCall pending_call = QDBusConnection::sessionBus().asyncCall(message);
    QDBusPendingCallWatcher *watcher = new QDBusPendingCallWatcher(pending_call, this);

    QObject::connect(watcher, &QDBusPendingCallWatcher::finished, this, [this](QDBusPendingCallWatcher *call){
        QDBusPendingReply<QString> reply = *call;

        if (reply.isError()){

            qWarning() << "GetCurrentFile D-Bus call failed:" << reply.error().message();
            call->deleteLater();
            return;
        }

        QString new_current_file = reply.value();

        if (m_currentFile != new_current_file){
            m_currentFile = new_current_file;

            emit stateChanged();
        }

        call->deleteLater();
    });
}

void BackendBridge::requestSyncPhase(){

    QDBusMessage message = QDBusMessage::createMethodCall(SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME, QStringLiteral("GetSyncPhase"));
    QDBusPendingCall pending_call = QDBusConnection::sessionBus().asyncCall(message);
    QDBusPendingCallWatcher *watcher = new QDBusPendingCallWatcher(pending_call, this);

    QObject::connect(watcher, &QDBusPendingCallWatcher::finished, this, [this](QDBusPendingCallWatcher *call){
        QDBusPendingReply<QString> reply = *call;

        if (reply.isError()){

            qWarning() << "GetSyncPhase D-Bus call failed:" << reply.error().message();
            call->deleteLater();

            return;
        }

        QString new_sync_phase = reply.value();

        if (m_syncPhase != new_sync_phase){
            m_syncPhase = new_sync_phase;

            emit stateChanged();
        }

        call->deleteLater();
    });
}

void BackendBridge::requestRootFolders(){

    QDBusMessage message = QDBusMessage::createMethodCall(SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME, QStringLiteral("GetRootFolders"));
    QDBusPendingCall pending_call = QDBusConnection::sessionBus().asyncCall(message);
    QDBusPendingCallWatcher *watcher = new QDBusPendingCallWatcher(pending_call, this);

    QObject::connect(watcher, &QDBusPendingCallWatcher::finished, this, [this](QDBusPendingCallWatcher *call){
        QDBusPendingReply<QStringList> reply = *call;

        if (reply.isError()){
            qWarning() << "GetRootFolders D-Bus call failed:" << reply.error().message();

            call->deleteLater();

            return;
        }

        m_rootFolders = reply.value();
        emit foldersChanged();
        call->deleteLater();
    });
}

void BackendBridge::requestSyncFolders(){
    QDBusMessage message = QDBusMessage::createMethodCall(SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME, QStringLiteral("GetSyncPaths"));

    QDBusPendingCall pending_call = QDBusConnection::sessionBus().asyncCall(message);

    QDBusPendingCallWatcher *watcher = new QDBusPendingCallWatcher(pending_call, this);

    QObject::connect(watcher, &QDBusPendingCallWatcher::finished, this, [this](QDBusPendingCallWatcher *call){
        QDBusPendingReply<QStringList> reply = *call;

        if (reply.isError()){
            qWarning() << "GetSyncPaths D-Bus call failed:" << reply.error().message();

            call->deleteLater();

            return;
        }

        m_syncFolders = reply.value();
        emit foldersChanged();
        call->deleteLater();
    });
}


void BackendBridge::saveSyncFolders(const QVariantList &folders){
    QStringList folder_names;

    for (const QVariant &folder : folders){
        folder_names.append(folder.toString());
    }

    QDBusMessage message = QDBusMessage::createMethodCall(SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME, QStringLiteral("SetSyncPaths"));
    message << folder_names;
    QDBusPendingCall pending_call = QDBusConnection::sessionBus().asyncCall(message);
    QDBusPendingCallWatcher *watcher = new QDBusPendingCallWatcher(pending_call, this);

    QObject::connect(watcher, &QDBusPendingCallWatcher::finished, this, [this](QDBusPendingCallWatcher *call){
        QDBusPendingReply<QString> reply = *call;

        if (reply.isError()){
            m_folderMessage = "ERROR: " + reply.error().message();

            emit folderMessageChanged();
            call->deleteLater();

            return;
        }

        m_folderMessage = reply.value();

        emit folderMessageChanged();
        refreshFolders();

        call->deleteLater();
    });
}

void BackendBridge::callMethod(const QString &method){
    QDBusMessage message = QDBusMessage::createMethodCall(SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME, method);

    bool sent = QDBusConnection::sessionBus().send(message);

    if (!sent){
        qWarning() << "Could not send D-Bus method call:" << method;
    }
}