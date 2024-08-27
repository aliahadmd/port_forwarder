# Port Forwarder

Port Forwarder is a user-friendly GUI application built with Python and Tkinter that simplifies the process of managing SSH port forwarding. It allows users to easily add, remove, and monitor forwarded ports, making it ideal for developers and system administrators who frequently work with remote servers.

## Features

- Add and remove ports for forwarding
- Start and stop port forwarding with a single click
- Real-time status updates for each port
- Built-in logging for troubleshooting
- Cross-platform compatibility (Windows, macOS, Linux)

## Requirements

- Python 3.6+
- Tkinter (usually comes pre-installed with Python)
- psutil

## Installation

Go to the [releases page](https://github.com/aliahadmd/port_forwarder/releases) and download the latest version. Then run exe file.


## Usage

1. Launch the application.
2. Enter a port number in the "Port" field and click "Add Port".
3. Repeat step 2 for all ports you want to forward.
4. Click "Start Forwarding" to begin the SSH port forwarding process.
5. Monitor the status of each port in the list view.
6. Use the log display at the bottom for detailed information and troubleshooting.
7. Click "Stop Forwarding" to terminate all port forwarding processes.

## Building Executable

To create a standalone executable, use PyInstaller:

1. Install PyInstaller:
   ```
   pip install -r requirements.txt
   ```

2. Build the executable:
   ```
   pyinstaller .\port_forwarder.spec
   ```

The executable will be created in the `dist` folder.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.











