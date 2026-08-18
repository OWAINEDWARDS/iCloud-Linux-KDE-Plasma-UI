#include "icloudlinux_plugin.h"
#include "backend_bridge.h"

#include <QQmlEngine>


void ICloudLinuxPlugin::registerTypes(const char *uri){

    Q_ASSERT(QString::fromLatin1(uri) == QStringLiteral("org.icloudlinux.backend"));

    qmlRegisterType<BackendBridge>(uri, 1, 0, "BackendBridge");
}