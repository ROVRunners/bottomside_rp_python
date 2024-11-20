import platform

import bottomside.main_system as main_system

if __name__ == '__main__':
    # Create an instance of the MainSystem class.
    main_system = main_system.MainSystem(platform.system())

    while main_system.run:
        try:
            main_system.loop()

        except KeyboardInterrupt as e:
            print(f'Exception in main_system.main_loop():\n{e}')
            main_system.shutdown()
