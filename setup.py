from setuptools import setup

package_name = 'jetrover_agent'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/agent.yaml']),
        ('share/' + package_name + '/launch', ['launch/agent.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@example.com',
    description='Semantic LLM robot agent for JetRover.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'world_model_node = jetrover_agent.world_model_node:main',
            'perception_node = jetrover_agent.perception_node:main',
            'planner_node = jetrover_agent.planner_node:main',
            'executor_node = jetrover_agent.executor_node:main',
            'explorer_node = jetrover_agent.explorer_node:main',
            'cli_command = jetrover_agent.cli_command:main',
        ],
    },
)
