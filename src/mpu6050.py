import ustruct


class MPU6050:
    def __init__(self, i2c, addr=0x68, threshold=1):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(self.addr, 0x6B, b"\x00")

        self.threshold_x = self.threshold_y = self.threshold_z = threshold

        print("MPU6050 sensor initialized")

    def get_acceleration(self, calibrated=True):
        data = self.i2c.readfrom_mem(self.addr, 0x3B, 6)
        x, y, z = ustruct.unpack(">hhh", data)

        if calibrated:
            return {
                "x": x / 16384.0 - self.offsets["x"],
                "y": y / 16384.0 - self.offsets["y"],
                "z": z / 16384.0 - self.offsets["z"],
            }
        else:
            return {"x": x / 16384.0, "y": y / 16384.0, "z": z / 16384.0}

    def get_gyro(self):
        data = self.i2c.readfrom_mem(self.addr, 0x43, 6)
        x, y, z = ustruct.unpack(">hhh", data)
        return {"x": x / 131.0, "y": y / 131.0, "z": z / 131.0}

    def get_temp(self):
        data = self.i2c.readfrom_mem(self.addr, 0x41, 2)
        (temp_raw,) = ustruct.unpack(">h", data)
        return temp_raw / 340.0 + 36.53

    def calibrate(self, samples=127):

        offsets = {"x": 0, "y": 0, "z": 0}

        for _ in range(samples):
            accel = self.get_acceleration(calibrated=False)
            offsets["x"] += accel["x"]
            offsets["y"] += accel["y"]
            offsets["z"] += accel["z"]

        offsets["x"] /= samples
        offsets["y"] /= samples
        offsets["z"] /= samples

        offsets["z"] -= 9.8

        self.offsets = offsets

        print("MPU 6050 calibration completed.")

    def is_moving(self):

        acc = self.get_acceleration(calibrated=True)

        x, y, z = acc["x"], acc["y"], acc["z"]

        if x >= self.threshold_x or x <= -1 * self.threshold_x:
            return acc

        elif y >= self.threshold_y or y <= -1 * self.threshold_y:
            return acc

        elif z >= 9.8 + self.threshold_z or z <= -9.8 - self.threshold_z:
            return acc

        else:
            return False
