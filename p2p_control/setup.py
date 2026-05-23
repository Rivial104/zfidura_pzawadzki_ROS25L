from setuptools import find_packages, setup

package_name = 'p2p_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rivial',
    maintainer_email='pawel.zawadzki9.stud@pw.edu.pl',
    description='Point-to-point action control for the 3-DOF manipulator',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'p2p_server = p2p_control.p2p_server:main',
            'p2p_client = p2p_control.p2p_client:main',
        ],
    },
)
