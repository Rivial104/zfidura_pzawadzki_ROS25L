from setuptools import find_packages, setup

package_name = 'gripper_ctrl'

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
    maintainer_email='rivial104i300@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'service = gripper_ctrl.gripper_control:main',
            'client = gripper_ctrl.gripper_client:main',
            'inv_kin = gripper_ctrl.inv_kin_tester:main'
        ],
    },
)
