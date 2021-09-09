# Simple driver for the EZO pH Circuit

class ATLASI2C:
    MEASUREMENT_TIME = const(120)

    def __init__(self, i2c, addr=99, period=150):
        self.i2c = i2c
        self.period = period
        self.addr = addr
        self.time = 0
        self.value = 0
        #self.i2c.writeto(addr, bytes([0x10])) # start continuos 1 Lux readings every 120ms
    
    def write(self, cmd):
        # appends the null character and sends the string over I2C
        cmd += "\00"
        self.i2c.writeto(self.addr, cmd)
    
    def read(self, num_of_bytes=31):
        self.time += self.period
        if self.time >= MEASUREMENT_TIME:
            self.time = 0
            data = self.i2c.readfrom(self.addr, num_of_bytes)
            response = list(filter(lambda x: x != 0, list(data))) # remove the null characters to get the response
            if response[0] == 1:             # if the response isn't an error
			    self.value = float(bytes(response[1:]).decode('ascii'))
            else:
                self.value = -1 #Error
            #self.value = (((data[0] << 8) + data[1]) * 1200) // 1000
        return self.value