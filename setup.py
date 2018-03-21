"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2018 Laurent Labatut / Laurent Champagnac
#
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# ===============================================================================
"""
from distutils.core import setup

import re
from setuptools import find_packages


def requirement_read(req_file):
    """
    Doc
    :param req_file: Doc
    :return: Doc
    """
    local_req_list = list()
    local_dep_list = list()
    for row_buffer in open(req_file).readlines():
        # Skip empty
        if len(row_buffer.strip()) == 0:
            continue
        # Skip "- ..."
        elif re.match("^-", row_buffer):
            continue
        # Skip "# ..."
        elif re.match("^#", row_buffer):
            continue
        # Git stuff (direct)
        # From : https://github.com/pypa/pip/issues/3610#issuecomment-356687173
        elif re.match("^git", row_buffer):
            pkg = row_buffer.split('#')[-1]
            local_dep_list.append(row_buffer.strip() + '-9876543210')
            local_req_list.append(pkg.replace('egg=', '').rstrip())
        else:
            # Ok
            local_req_list.append(row_buffer)

    print("local_req_list={0}".format(local_req_list))
    print("local_dep_list={0}".format(local_dep_list))
    return local_req_list, local_dep_list


# ===========================
# SETUP
# ===========================

p_name = "resolvusclient"
p_author = "Laurent Champagnac"
p_email = "champagnac.laurent@gmail.com"
p_url = "https://knock.center"
p_version = "0.0.1"

# Load
req_list, dep_list = requirement_read("requirements.txt")
test_req_list, _ = requirement_read("requirements_test.txt")

setup(

    # Project details
    name=p_name,
    author=p_author,
    author_email=p_email,
    url=p_url,
    description="resolvus client",

    # Version, format : Major.Minor.Revision
    version=p_version,

    # Packages
    packages=find_packages(exclude=["*_test*", "_*"]),
    include_package_data=True,

    # License & read me
    license=open("LICENSE.txt").read(),
    long_description=open("README.md").read(),

    # Data files
    data_files=[
        ("", ["requirements_test.txt", "requirements.txt", "README.md", "LICENSE.txt"]),
    ],

    # Classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries",
        "Natural Language :: English",
    ],

    # Dependencies
    install_requires=req_list,

    # Direct deps
    dependency_links=dep_list,

    # Dependencies : test
    tests_require=test_req_list,

    # Zip
    zip_safe=False,
)
