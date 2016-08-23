# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ontheway
                                 A QGIS plugin
 Calculate route
                             -------------------
        begin                : 2016-08-18
        copyright            : (C) 2016 by Adam Borczyk
        email                : ad.borczyk@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ontheway class from file ontheway.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ontheway import ontheway
    return ontheway(iface)
