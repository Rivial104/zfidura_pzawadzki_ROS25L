from setuptools import find_packages, setup
import os 
from glob import glob 

package_name = 'pose_subscriber'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*')))],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rivial',
    maintainer_email='rivial104i300@gmail.com',
    description='Lecture 2',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pose_sub = pose_subscriber.pose_sub:main',
            'auto_p = pose_subscriber.template:main',
        ],
    },
)
