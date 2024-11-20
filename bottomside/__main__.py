import bottomside.main_system as rov

if __name__ == '__main__':
    # Set to True to close the program when the ROV exits without an error through modifying ROV.run.
    intentionally_shut_down = False

    # Create an instance of the ROV class.
    main_system = rov.ROV()

    while main_system.run:
        try:
            main_system.loop()

        except KeyboardInterrupt as e:
            print(f'Exception in main_system.main_loop():\n{e}')
            main_system.shutdown()
            intentionally_shut_down = True
