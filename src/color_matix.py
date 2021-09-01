import DobotDllTypeX as dTypeX
from threading import Thread
import time
import serial
import operator


def ColorDetect():
    '''Function used to read the serial message from the JeVois camera. A colour buffer is filled based
     on the times each colour, red, green or blue is detected. The most frequent colour is then returned'''
    global total_time_colour

    serdev = 'COM5'  # serial device of JeVois 1

    start = time.perf_counter()
    dict = {'Red': 0, 'Green': 0, 'Blue': 0}

    with serial.Serial(serdev, 115200, timeout=1) as ser:
        while 1:
            # Read a whole line and strip any trailing line ending character:
            line = ser.readline().rstrip().decode()
            if line == 'Blue' or line == 'Green' or line == 'Red':
                dict[line] += 1  # add one to the value of the dictionary associated with that color

            if dict['Red'] == 40 or dict['Green'] == 40 or dict['Blue'] == 40:
                decision = max(dict.items(), key=operator.itemgetter(1))[0]
                all_values = dict.values()
                max_value = max(all_values)
                print(f'Colour detected: {decision}')
                print(f'Times detected: {max_value}')
                finish = time.perf_counter()
                total = finish - start
                total_time_colour += total
                return decision

            finish = time.perf_counter()
            timer = round(finish - start, 2)  # get the total time taken by the function if no color is detected

            if timer >= 6:  # protect against infinite loops
                print(f'Time elapsed in colour sensor: {timer} second(s)')
                print('No color detected...')
                return None


def calibrate(api):
    '''Get the location of the End effector, Used to callibrate the Dobot's parameters below'''
    x = dTypeX.GetPose(api)[0]
    y = dTypeX.GetPose(api)[1]
    z = dTypeX.GetPose(api)[2]
    return x,y,z


def INITIALIZE_PickandPlace(api):
    '''Initialise the Pick and Place parameters used'''
    global arm_speed, belt_speed, HomeX, HomeY, HomeZ, PickX, PickY, \
        PickZ, StartX, StartY, StartZ, EndX, EndY, EndZ, i, j,x_reset,y_reset

    # Home Position. This is the reference point of our program
    HomeX = 130
    HomeY = 0
    HomeZ = 80

    # Origin of Cube Matrix
    PickX = 123.3771743774414
    PickY = 104.88229370117188
    PickZ = -43  # same for all
    x_reset = PickX  # reset the coordinates after 2 updates
    y_reset = PickY  # reset the coordinates after 2 updates

    # Conveyor Belt Start Block Position
    StartX = 216.45199584960938
    StartY = 120.03961181640625
    StartZ = 18

    # Conveyor Belt End Block Position
    EndX = 214.4
    EndY = -120
    EndZ = 16

    # Speeds
    arm_speed = 400
    belt_speed = 50

    # Steps
    i = 1
    j = 1

    # Set
    dTypeX.SetEndEffectorParamsEx(api, 0, 0, 0, 1)
    dTypeX.SetPTPCoordinateParams(api,  arm_speed, arm_speed, arm_speed, arm_speed, 1)


def INITIALIZE_Sorting():
    '''Initialize the sorting parameters used'''

    global HomeX, HomeY, HomeZ, RedX, RedY, RedZ, GreenX, GreenY, GreenZ, BlueX, BlueY, BlueZ,\
        red_count, blue_count, green_count, calibration, total_time_belt, total_time_arm, \
        threading_time, total_time_colour, exec_time_sort, sleep, time_slept

    #Green Place
    GreenX = 127.95995330810547
    GreenY = -150.52438354492188
    GreenZ = -40

    #Red Place
    RedX = 100.7859115600586
    RedY = -145.68092346191406
    RedZ = -40

    #Blue Place
    BlueX = 73.11555480957031
    BlueY = -140.59437561035156
    BlueZ = -40

    # Store count
    red_count = 0
    green_count = 0
    blue_count = 0
    calibration = 0
    total_time_colour = 0
    total_time_belt = 0
    total_time_arm = 0
    exec_time_sort = 0
    time_slept = 7.2  # initial offset due to all constant sleeps between the suction cup on/off
    sleep = 0
    threading_time = 4  # initial threading wait in the move_and_sort function


def updateY(xval, yval):
    """Update the y value in the matrix. This is done once every 2 x_value updates"""
    global j, PickX, PickY
    m = j % 3
    PickX = xval + 2
    PickY = yval + 21
    j += 1


def updateX(xval, yval):
    """Update the PickX and PickY value in the matrix. This is the location of the next box"""
    global i, PickX, PickY, m
    m = i % 3
    PickX = xval - 21  # step in x
    PickY = yval - 4  # step in y
    if i == 3:
        PickX = x_reset  # reset x value to start from the beginning
        PickY = y_reset  # reset y value to start from the beginning
        updateY(PickX, PickY)  # take one step in the y direction
    if i == 6:
        PickX = x_reset  # reset x value to start from the beginning
        PickY = y_reset  # reset y value to start from the beginning
        updateY(PickX, PickY)  # take one step in the y direction
        updateY(PickX, PickY)  # take one step in the y direction
    i += 1


def pick_and_place(api):
    global PickX, PickY, PickZ, StartX, StartY, StartZ, EndX, EndY, EndZ, HomeX, HomeY, HomeZ, total_time_arm

    start = time.perf_counter()

    cubes = 9
    # pick first cube
    dTypeX.SetPTPCmdEx(api, 2, PickX, PickY, PickZ+10, 0, 1)
    dTypeX.SetPTPCmdEx(api, 2, PickX, PickY, PickZ, 0, 1)
    time.sleep(0.1)
    dTypeX.SetEndEffectorSuctionCupEx(api, 1, 1)
    time.sleep(0.1)
    dTypeX.SetPTPCmdEx(api, 2, PickX, PickY, StartZ+15, 0, 1)
    dTypeX.SetPTPCmdEx(api, 2, StartX, StartY, StartZ, 0, 1)  # start position of block
    time.sleep(0.1)
    dTypeX.SetEndEffectorSuctionCupEx(api, 0, 1)
    time.sleep(0.1)
    dTypeX.SetPTPCmdEx(api, 2, StartX, StartY, StartZ+10, 0, 1)
    if cubes > 1:
        updateX(PickX, PickY)  # get the new values of the x-axis cube
        cubes -= 1

    finish = time.perf_counter()
    total = finish - start
    total_time_arm += total


def test_pick_and_place(api):
    '''Pick and Place without the sunction cup for easier calibration'''
    global PickX, PickY, PickZ, StartX, StartY, StartZ, EndX, EndY, EndZ, HomeX, HomeY, HomeZ
    cubes = 9
    # pick first cube
    dTypeX.SetPTPCmdEx(api, 2, PickX, PickY, PickZ+10, 0, 1)
    dTypeX.SetPTPCmdEx(api, 2, PickX, PickY, PickZ, 0, 1)
    dTypeX.SetPTPCmdEx(api, 2, PickX, PickY, PickZ+10, 0, 1)
    if cubes > 1:
        updateX(PickX, PickY)  # get the new values of the x-axis cube
        cubes -= 1


def test_pap(api):
    'Hover around the whole matrix to calibrate'
    start = time.perf_counter()
    for _ in range(9):
        test_pick_and_place(api)
    finish = time.perf_counter()
    total = finish - start
    print(total)


def Sorting(api, decision):
    '''Sorts the boxes based on the colour. If no colour is detected the Dobot
    returns to the Home position and it is disconnected in order to re-calibrate it'''

    global HomeX, HomeY, HomeZ, RedX, RedY, RedZ, GreenX, GreenY, GreenZ, BlueX, BlueY, BlueZ, \
        red_count, blue_count, green_count, calibration, total_time_arm, total_time_colour

    start = time.perf_counter()

    dTypeX.SetPTPCmdEx(api, 2, EndX, EndY, EndZ, 0, 1)
    time.sleep(0.1)
    dTypeX.SetEndEffectorSuctionCupEx(api, 1, 1)
    time.sleep(0.1)
    dTypeX.SetPTPCmdEx(api, 2, EndX, EndY, EndZ+5, 0, 1)

    if decision == 'Red':
        dTypeX.SetPTPCmdEx(api, 2, RedX, RedY, EndZ + 5, 0, 1)
        dTypeX.SetPTPCmdEx(api, 2, RedX, RedY, RedZ, 0, 1)
        RedX -= 3
        RedY += 25
        red_count += 1

    elif decision == 'Green':
        dTypeX.SetPTPCmdEx(api, 2, GreenX, GreenY, EndZ + 5, 0, 1)
        dTypeX.SetPTPCmdEx(api, 2, GreenX, GreenY, GreenZ, 0, 1)
        GreenX -= 3
        GreenY += 25
        green_count += 1

    elif decision == 'Blue':
        dTypeX.SetPTPCmdEx(api, 2, BlueX, BlueY, EndZ + 5, 0, 1)
        dTypeX.SetPTPCmdEx(api, 2, BlueX, BlueY, BlueZ, 0, 1)
        BlueX -= 3
        BlueY += 25
        blue_count += 1

    elif decision == None:
        # if None of red, green or blue is detected
        calibration += 1
        total_time_colour += 6
        dTypeX.SetPTPCmdEx(api, 0, HomeX, HomeY, HomeZ, 0, 1)
        time.sleep(0.1)
        print('Calibrate the JeVois Camera')
        dTypeX.SetEndEffectorSuctionCupEx(api, 0, 1)
        dTypeX.DisconnectDobot(api)
        return

    time.sleep(0.1)
    dTypeX.SetEndEffectorSuctionCupEx(api, 0, 1)
    time.sleep(0.1)
    x, y, z = calibrate(api)
    dTypeX.SetPTPCmdEx(api, 2, x, y, z + 10, 0, 1)

    finish = time.perf_counter()
    total = finish - start
    total_time_arm += total


def move_belt(api):
    '''Function used to move the belt when a block is placed on the starting position'''
    global total_time_belt, exec_belt, sleep

    start = time.perf_counter()

    distance = 298*150  # distance belt block covered along the y-axis
    STEP_PER_CRICLE = 360.0 / 1.8 * 10.0 * 16.0
    MM_PER_CRICLE = 3.1415926535898 * 36.0
    vel = float(belt_speed) * STEP_PER_CRICLE / MM_PER_CRICLE
    dTypeX.SetEMotorSEx(api, 0, 1, int(vel), int(distance), 1)

    finish = time.perf_counter()
    exec_belt = finish - start
    sleep = exec_belt
    print(f'time to move belt{exec_belt}')
    total_time_belt += exec_belt


def calibrate_belt(api):
    '''Function used to calibrate the belt Starting and Stopping position'''

    dTypeX.SetPTPCmdEx(api,2,StartX,StartY, StartZ+5,0,1)
    time.sleep(2)

    x,y,z = calibrate(api)
    dTypeX.SetPTPCmdEx(api, 2, x, y, z+5, 0, 1)
    time.sleep(1)
    dTypeX.SetPTPCmdEx(api, 2, x, y, z, 0, 1)
    time.sleep(1)
    dTypeX.SetPTPCmdEx(api, 2, x, y, z+5, 0, 1)
    time.sleep(1)
    move_belt(api)
    print('--- Adjust Arm Manually ---')
    time.sleep(15)
    x,y,z =calibrate(api)
    dTypeX.SetPTPCmdEx(api, 2, x, y, z+5, 0, 1)
    dTypeX.SetPTPCmdEx(api, 2, x, y, z, 0, 1)
    dTypeX.SetPTPCmdEx(api, 2, x, y, z + 5, 0, 1)


def move_arm(api):
    global total_time_arm

    start = time.perf_counter()

    dTypeX.SetPTPCmdEx(api, 2, EndX, EndY, EndZ + 10, 0, 1)

    finish = time.perf_counter()
    exec_arm = finish - start
    print(f'time to move arm {exec_arm}')
    total_time_arm += exec_arm


def move_and_sort(api):
    global HomeX, HomeY, HomeZ, RedX, RedY, RedZ, GreenX, GreenY, GreenZ, BlueX, BlueY, BlueZ, \
        red_count, blue_count, green_count, threading_time, exec_time_sort, time_slept

    start = time.perf_counter()

    t1 = Thread(target=move_belt, args=[api])
    t2 = Thread(target=move_arm, args=[api])

    t1.start()
    t2.start()

    if True:
        time.sleep(threading_time)  # threading time is the optimised time after the first cube is sorted.
        threading_time = 0
        threading_time = sleep + 0.1  # get the optimised threading time to minimise the time wasted
        time_slept += threading_time
        print('JeVois Starting...')
        Sorting(api, ColorDetect())

    t1.join()
    t2.join()

    finish = time.perf_counter()
    exec_time = finish - start
    exec_time_sort += exec_time
    print(f"--- Sorting {round(exec_time, 2)} second(s) ---")


def main():
    global total_time_belt, total_time_arm, total_time

    CON_STR = {
        dTypeX.DobotConnect.DobotConnect_NoError: "DobotConnect_NoError",
        dTypeX.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
        dTypeX.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

    api = dTypeX.load()
    state = dTypeX.ConnectDobot(api, 'COM3', 115200)
    print("Connect status:", CON_STR[state[0]])

    INITIALIZE_PickandPlace(api)
    INITIALIZE_Sorting()

    switch = True
    i = 0

    start = time.perf_counter()

    while switch:
        pick_and_place(api)
        total_time_belt += move_and_sort(api)
        i += 1
        if i == 9:
            print('Dobot Finished')
            print(f'Red count: {red_count}')
            print(f'Blue count: {blue_count}')
            print(f'Green count: {green_count}')
            print(f'Calibrations needed: {calibration}')
            switch = False
            dTypeX.SetPTPCmdEx(api, 2, HomeX, HomeY, HomeZ, 0, 1)
            dTypeX.DisconnectAll()

    finish = time.perf_counter()
    t = finish - start
    total = total_time_arm + total_time_belt + total_time_colour

    print(f'Actual time: {round(t, 2)} seconds at arm speed {arm_speed} and belt speed {belt_speed}')
    print(f'Elapsed time: {round(total, 2)} seconds at arm speed {arm_speed} and belt speed {belt_speed}')
    print(f'Time saved due to threading: {round(total-t, 2)} seconds ')
    print(f'Total time in move_and_sort: {round(exec_time_sort, 2)} seconds ')
    print(f'Total time to move belt: {round(total_time_belt, 2)} seconds ({round(100*(total_time_belt)/total, 2)}%)')
    print(f'Total time to move arm: {round(total_time_arm, 2)} seconds ({round(100*(total_time_arm)/total,2)}%)')
    print(f'Total time in colour sensor: {round(total_time_colour, 2)} seconds ({round(100 * (total_time_colour) / total,2)}%)')
    print(f'time delays: {round(time_slept, 2)}')


if __name__ == "__main__":
  main()