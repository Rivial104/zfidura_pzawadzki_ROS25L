from setuptools import find_packages, setup

package_name = 'drawing_shape'

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
    description='Action server for drawing trajectories with the manipulator',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'drawing_action_server_exe = drawing_shape.drawing_action_server:main',
            'robot_status = drawing_shape.drawing_action_status:main',
            'rviz_marker_example = drawing_shape.rviz_marker_example:main',
        ],
    },
)
