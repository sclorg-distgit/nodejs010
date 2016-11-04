%global scl_name_base nodejs
%global scl_name_version 010
 
%global scl %{scl_name_base}%{scl_name_version}

%scl_package %scl
%global install_scl 1

# do not produce empty debuginfo package
%global debug_package %{nil}

Summary: %scl Software Collection
Name: %scl_name
Version: 2.1
Release: 5.sc1%{?dist}

Source1: macros.nodejs
Source2: nodejs.attr
Source3: nodejs.prov
Source4: nodejs.req
Source5: nodejs-symlink-deps
Source6: nodejs-fixdep
Source7: nodejs_native.attr
Source8: README
Source9: LICENSE
Source10: multiver_modules

License: MIT

%if 0%{?install_scl}
Requires: %{scl_prefix}nodejs
Requires: %{scl_prefix}npm
Requires: %{scl_prefix}runtime
%endif

BuildRequires: scl-utils-build
BuildRequires: python-devel
BuildRequires: help2man

%description
This is the main package for %scl Software Collection.

%package runtime
Summary: Package that handles %scl Software Collection.
Requires: %{_root_bindir}/scl_source

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary: Package shipping basic build configuration
Requires: scl-utils-build

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%package scldevel
Summary: Package shipping development files for %scl
 
%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.

%prep
%setup -c -T

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE8})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE9} .

%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF

chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_scl_scripts}/root
cat >> %{buildroot}%{_scl_scripts}/enable << EOF
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export LD_LIBRARY_PATH=%{_libdir}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
export PYTHONPATH=%{_scl_root}%{python_sitelib}\${PYTHONPATH:+:\${PYTHONPATH}}
export MANPATH=%{_mandir}:\$MANPATH
. scl_source enable v8314
EOF

# install rpm magic
install -Dpm0644 %{SOURCE1} %{buildroot}%{_root_sysconfdir}/rpm/macros.%{name}
install -Dpm0644 %{SOURCE2} %{buildroot}%{_rpmconfigdir}/fileattrs/%{name}.attr
install -pm0755 %{SOURCE3} %{buildroot}%{_rpmconfigdir}/%{name}.prov
install -pm0755 %{SOURCE4} %{buildroot}%{_rpmconfigdir}/%{name}.req
install -pm0755 %{SOURCE5} %{buildroot}%{_rpmconfigdir}/%{name}-symlink-deps
install -pm0755 %{SOURCE6} %{buildroot}%{_rpmconfigdir}/%{name}-fixdep
install -Dpm0644 %{SOURCE7} %{buildroot}%{_rpmconfigdir}/fileattrs/%{name}_native.attr
install -Dpm0644 %{SOURCE10} %{buildroot}%{_datadir}/node/multiver_modules

cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

# some packages in the nodejs SCL still include ExcludeArch: %%{nodejs_arches},
# which is not defined in el6 (in el7 it is defined in redhat-rpm-macros), so
# we need to add it here, otherwise packages have problem in mash
%if 0%{?rhel} <= 6
echo "%%nodejs_arches %%{ix86} x86_64 %%{arm}" >>%{buildroot}%{_root_sysconfdir}/rpm/macros.%{name}
%endif

# ensure Requires are added to every native module that match the Provides from
# the nodejs build in the buildroot
cat << EOF > %{buildroot}%{_rpmconfigdir}/%{name}_native.req
#!/bin/sh
echo 'nodejs010-nodejs(abi) = %nodejs_abi'
echo 'nodejs010-nodejs(v8-abi) = %v8_abi'
EOF
chmod 0755 %{buildroot}%{_rpmconfigdir}/%{name}_native.req

cat << EOF > %{buildroot}%{_rpmconfigdir}/%{name}-require.sh
#!/bin/sh
%{_rpmconfigdir}/%{name}.req $*
%{_rpmconfigdir}/find-requires $*
EOF
chmod 0755 %{buildroot}%{_rpmconfigdir}/%{name}-require.sh

cat << EOF > %{buildroot}%{_rpmconfigdir}/%{name}-provide.sh
#!/bin/sh
%{_rpmconfigdir}/%{name}.prov $*
%{_rpmconfigdir}/find-provides $*
EOF
chmod 0755 %{buildroot}%{_rpmconfigdir}/%{name}-provide.sh

%scl_install
# scl doesn't include this directory
mkdir -p %{buildroot}%{_scl_root}%{python_sitelib}
mkdir -p %{buildroot}%{_libdir}/pkgconfig

# install generated man page
mkdir -p %{buildroot}%{_mandir}/man7/
install -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7

%files

%files runtime
%doc README LICENSE
%scl_files
%dir %{_scl_root}%{python_sitelib}
%dir %{_libdir}/pkgconfig
%{_datadir}/node/multiver_modules
%{_mandir}/man7/%{scl_name}.*

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config
%{_root_sysconfdir}/rpm/macros.%{name}
%{_rpmconfigdir}/fileattrs/%{name}*.attr
%{_rpmconfigdir}/%{name}*

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Thu Jan 14 2016 Tomas Hrcka <thrcka@redhat.com> - 2.1-5
- Include nodemon in collection
- Update packaging scripts and macros

* Sun Oct 04 2015 Zuzana Svetlikova <zsvetlik@redhat.com> - 2.1-3
- Enable installing of whole collection

* Thu Jul 02 2015 Tomas Hrcka <thrcka@redhat.com> - 2.1-2
- RHSCL 2.1 release
- disable installing of whole collection this will be enabled after devel period

* Thu May 14 2015 Tomas Hrcka <thrcka@redhat.com> - 2.0-3
- Red Hat Software collections 2.0
- Own python modules directory

* Wed Oct 08 2014 Tomas Hrcka <thrcka@redhat.com> - 1.2-29
- Require scriptlet scl_devel from root_bindir not scl_bindir 

* Mon Oct 06 2014 Tomas Hrcka <thrcka@redhat.com> - 1.2-27
- Require scriptlet scl_devel instead of specific scl-utils version

* Mon Sep 08 2014 Tomas Hrcka <thrcka@redhat.com> - 1.2-26
- Fix version of scl-utils required by this package
- Bump version

* Mon Mar 31 2014 Honza Horak <hhorak@redhat.com> - 1.1-25
- Fix path typo in README
  Related: #1061452

* Mon Feb 17 2014 Tomas Hrcka <thrcka@redhat.com> - 1.1-24
- Require version of scl-utils 

* Wed Feb 12 2014 Tomas Hrcka <thrcka@redhat.com> - 1.1-23
- Define scl_name_base and scl_name_version macros 

* Wed Feb 12 2014 Honza Horak <hhorak@redhat.com> - 1.1-22
- Some more grammar fixes in README
  Related: #1061452

* Wed Feb 12 2014 Tomas Hrcka <thrcka@redhat.com> - 1.1-21
- Add nodejs010-scldevel sub package

* Tue Feb 11 2014 Tomas Hrcka <thrcka@redhat.com> - 1.1-20
- Add LICENSE, README and nodejs010.7 man page
- Minor changes in collection macros nodejs-fixdep,nodejs-symlink-deps

* Thu Dec 05 2013 Tomas Hrcka <thrcka@redhat.com> - 1-20
- install collection packages as dependencies

* Wed Nov 27 2013 Tomas Hrcka <thrcka@redhat.com> - 1-19
- rebuilt
- fiw v8314 dependency

* Wed Nov 20 2013 Tomas Hrcka <thrcka@redhat.com> - 1-18
- added dependency on v8314 scl

* Thu Aug 15 2013 thrcka@redhat.com - 1-17
- clean up after previous fix

* Fri Aug 09 2013 thrcka@redhat.com - 1-16
- RHBZ#993425 - nodejs010.req fails when !noarch 

* Mon Jun 03 2013 thrcka@redhat.com - 1-15
- Changed licence to MIT

* Thu May 23 2013 Tomas Hrcka <thrcka@redhat.com> - 1-14.1
- fixed typo in MANPATH

* Thu May 23 2013 Tomas Hrcka <thrcka@redhat.com> - 1-14
- Changed MAN_PATH so it does not ignore man pages from host system

* Thu May  9 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-13
- Remove colons forgotten in scriplets

* Tue May 07 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-12
- Add runtime dependency on scl-runtime

* Mon May 06 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-11
- Add pkgconfig file ownership

* Mon May 06 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-10
- Workaround scl-utils not generating all directory ownerships (#956213)

* Mon May 06 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-9
- Fix enable scriptlet evironment expansion (#956788)

* Wed Apr 17 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-8
- Extend MANPATH env variable
- Add npm to meta package requires

* Mon Apr 15 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-7
- Update macros and requires/provides generator to latest

* Wed Apr 10 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-6
- Fix rpm requires/provides generator paths
- Add requires to main meta package

* Mon Apr 08 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-5
- Make package architecture specific for libdir usage

* Mon Apr 08 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-4
- Add rpm macros and tooling

* Mon Apr 08 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-3
- Add proper scl-utils-build requires

* Fri Apr 05 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-2
- Add PYTHONPATH to configuration

* Tue Mar 26 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1-1
- Initial version of the Node.js Software Collection
