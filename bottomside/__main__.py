import bottomside.main_system as rov

if __name__ == '__main__':
    # Set to True to close the program when Spike exits without an error through modifying Spike.run.
    intentionally_shut_down = False

    while not intentionally_shut_down:
        try:
            # Create an instance of the Spike class.
            main_system = rov.ROV()

            # Loop until Spike.run is set to False, then close the program.
            while main_system.run:
                main_system.loop()

            intentionally_shut_down = True

        except Exception as e:
            print(f'Exception in main_system.main_loop():\n{e}')
