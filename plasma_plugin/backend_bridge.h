#pragma once

#include <QObject>
#include <QString>
#include <QStringList>
#include <QVariantList>


class BackendBridge : public QObject{
    Q_OBJECT

    Q_PROPERTY(QString status READ status NOTIFY stateChanged)
    Q_PROPERTY(bool syncing READ syncing NOTIFY stateChanged)
    Q_PROPERTY(QString currentFile READ currentFile NOTIFY stateChanged)
    Q_PROPERTY(QString syncPhase READ syncPhase NOTIFY stateChanged)

    Q_PROPERTY(QStringList rootFolders READ rootFolders NOTIFY foldersChanged)
    Q_PROPERTY(QStringList syncFolders READ syncFolders NOTIFY foldersChanged)
    Q_PROPERTY(QString folderMessage READ folderMessage NOTIFY folderMessageChanged)

public:
    explicit BackendBridge(QObject *parent = nullptr);

    QString status() const;
    bool syncing() const;
    QString currentFile() const;
    QString syncPhase() const;

    QStringList rootFolders() const;
    QStringList syncFolders() const;
    QString folderMessage() const;

    Q_INVOKABLE void refresh();
    Q_INVOKABLE void startService();
    Q_INVOKABLE void stopService();
    Q_INVOKABLE void restartService();
    Q_INVOKABLE void sync();

    Q_INVOKABLE void refreshFolders();
    Q_INVOKABLE void saveSyncFolders(const QVariantList &folders);

signals:
    void stateChanged();
    void foldersChanged();
    void folderMessageChanged();

private slots:
    void onStateChanged(const QString &status, bool syncing, const QString &currentFile, const QString &syncPhase);
    void onFoldersChanged(const QStringList &rootFolders, const QStringList &syncFolders);

private:
    void requestStatus();
    void requestSyncing();
    void requestCurrentFile();
    void requestSyncPhase();
    void requestRootFolders();
    void requestSyncFolders();

    void callMethod(const QString &method);

    QString m_status = "Unknown";
    bool m_syncing = false;
    QString m_currentFile = "—";
    QString m_syncPhase = "Idle";

    QStringList m_rootFolders;
    QStringList m_syncFolders;
    QString m_folderMessage;
};