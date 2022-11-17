import csv, sys

SENSOR2_THRESH = 3.00
tank_lb = 0.3
tank_ub = 5.81
bottle_ub = 0.9
refill = 10.0
input = sys.argv[1]
output = sys.argv[2]


with open(input, "r") as csvinput:
    with open(output, "w") as csvoutput:
        writer = csv.writer(csvoutput)
        for row in csv.reader(csvinput):
            if row[0] == "timestamp":
                writer.writerow(row + ["class"])
            else:
                if int(row[4]) == 1 and (
                    float(row[1]) <= tank_lb
                    or (float(row[2]) >= SENSOR2_THRESH and float(row[2]) != 999)
                    or (float(row[3]) >= bottle_ub and float(row[3]) != 999)
                ):
                    # print (row[2])

                    if float(row[2] == refill):
                        writer.writerow(row + ["Dos"])
                    elif float(row[2] == refill) or row[3] == "0.0":
                        writer.writerow(row + ["Normal"])
                    else:
                        writer.writerow(
                            row + ["Command Injection TH"]
                        )  # threshold based

                elif (
                    int(row[4]) == 0
                    and float(row[3]) < bottle_ub
                    and float(row[1]) > tank_lb
                ):
                    writer.writerow(row + ["Command Injection TL"])  # tank level based
                elif float(row[2]) == 999 or float(row[3]) == 999:
                    writer.writerow(row + ["DoS"])
                # we good
                else:
                    writer.writerow(row + ["Normal"])
