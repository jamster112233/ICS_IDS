f = open("RIAHistory.txt", 'w+')
f.write('START\n')
f.close()
while True:
    print("Response injection attack")
    print("Enter stealth level:")
    print("[n] - Do not modify")
    print("[1] - Blatantly obvious")
    print("[2] - Plausible")
    print("[3] - Harder to detect")
    print("[4] - Hard to detect")
    print("[q] - Quit")

    response = ''

    while response != 'n' and response != '1' and response != '2' and response != '3' and response != '4' and response != 'q':
        response = str(raw_input('>'))

    f = open("RIAttackMode.txt", "w+")
    h = open("RIAHistory.txt", "a")
    h.write(response + '\n')

    if response == 'q':
        f.write('n')
        f.close()
        exit(0)
    else:
        f.write(response)
        f.close()

    print("\n")

