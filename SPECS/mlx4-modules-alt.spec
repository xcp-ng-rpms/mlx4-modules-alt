%define vendor_name Mellanox
%define vendor_label mellanox
%define driver_name mlx4

# XCP-ng: install to the override directory
%define module_dir override

Summary: %{vendor_name} %{driver_name} device drivers
Name: mlx4-modules-alt
Version: 4.9_7.1.0.0
Release: 1%{?dist}
License: GPLv2

# Extracted from https://network.nvidia.com/products/ethernet-drivers/linux/mlnx_en/
Source0: mlx4-modules-alt-4.9_7.1.0.0.tar.gz

BuildRequires: gcc
BuildRequires: kernel-devel
Provides: vendor-driver
Requires: kernel-uname-r = %{kernel_version}
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

# To avoid conflicts, we don't ship mlx_compat.ko, so must require it through a virtual "Provides"
Requires: mlx_compat
Requires(post): mlx_compat

%description
%{vendor_name} %{driver_name} device drivers for the Linux Kernel
version %{kernel_version}.

%prep
%autosetup -p1 -n mlx4-modules-alt-%{version}

%build
export KSRC=/lib/modules/%{kernel_version}/build
export KVERSION=%{kernel_version}

find compat -type f -exec touch -t 200012201010 '{}' \; || true
./scripts/mlnx_en_patch.sh --without-mlx5 --without-mlxfw --kernel $KVERSION --kernel-sources $KSRC %{?_smp_mflags}
%{__make} V=0 %{?_smp_mflags}

%install
export INSTALL_MOD_PATH=%{buildroot}
export INSTALL_MOD_DIR=%{module_dir}
export KSRC=/lib/modules/%{kernel_version}/build
export KVERSION=%{kernel_version}

%{__make} install KSRC=$KSRC MODULES_DIR=$INSTALL_MOD_DIR DESTDIR=%{buildroot} KERNELRELEASE=$KVERSION DEPMOD=/bin/true
# Cleanup unnecessary kernel-generated module dependency files.
find %{buildroot}/lib/modules -iname 'modules.*' -exec rm {} \;

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -exec mv '{}' %{buildroot}/lib/modules/%{kernel_version}/%{module_dir} \;
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+x

%post
/sbin/depmod %{kernel_version}
%{regenerate_initrd_post}

%postun
/sbin/depmod %{kernel_version}
%{regenerate_initrd_postun}

%posttrans
%{regenerate_initrd_posttrans}

%files
/lib/modules/%{kernel_version}/%{module_dir}/mlx4*.ko
# Don't include mlx_compat.ko. We require it from another package instead
%exclude /lib/modules/%{kernel_version}/%{module_dir}/mlx_compat.ko

%changelog
* Mon Jun 17 2024 Gael Duperrey <gduperrey@vates.tech> - 4.9_7.1.0.0-1
- Initial package
- Require mlx_compat virtual provides instead of shipping mlx_compat.ko
