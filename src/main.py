from machine import Pin, SPI, I2C, Timer, PWM
from ili9341 import Display
from mpu6050 import MPU6050
import time
import os

# ----- Constants -----
CS_PIN_NUM = 26
DC_PIN_NUM = 25
RST_PIN_NUM = 4

SCK_PIN_NUM = 5
MOSI_PIN_NUM = 19
SPI_BAUD_RATE = 20000000
SPI_CHANNEL_NUM = 1

SCL_PIN_NUM = 14
SDA_PIN_NUM = 22
I2C_FREQ = 400000
I2C_CHANNEL_NUM = 0

PWM_FREQ = 1000
PWM_MAX_DUTY = 1023
BACKLIGHT_PIN_NUM = 13

MPU_READ_TIMER_NUM = 1
MPU_READ_PERIOD = 1000

IMAGES_DIR = "pictures"
IMAGE_NAMES = [name for name in os.listdir(f"/{IMAGES_DIR}")]
IMAGE_FILENAMES = [f"{IMAGES_DIR}/{name}" for name in IMAGE_NAMES]


# ----- Global Variables -----
spi = None
display = None
mpu = None
i2c = None
mpu_read_timer = None
pwm = None
shake_detected = False
current_pic_index = 0


def setup_spi():
    """Set up SPI for communicating with the TFT display"""

    global spi
    spi = SPI(
        SPI_CHANNEL_NUM,
        baudrate=SPI_BAUD_RATE,
        sck=Pin(SCK_PIN_NUM),
        mosi=Pin(MOSI_PIN_NUM),
        polarity=0,
        phase=0,
    )


def setup_i2c():
    """Set up I2C for communnicating with the MPU6050"""

    global i2c
    i2c = I2C(
        I2C_CHANNEL_NUM, scl=Pin(SCL_PIN_NUM), sda=Pin(SDA_PIN_NUM), freq=I2C_FREQ
    )


def setup_display():
    """
    Set up the display driver using SPI

    Note:
        SPI MUST be configured before calling this function
    """

    global display, spi

    cs = Pin(CS_PIN_NUM, Pin.OUT)
    dc = Pin(DC_PIN_NUM, Pin.OUT)
    rst = Pin(RST_PIN_NUM, Pin.OUT)

    display = Display(spi=spi, cs=cs, dc=dc, rst=rst)


def setup_mpu():
    """
    Set up the MPU driver using I2C

    Note:
        I2C MUST be configured before calling this function
    """

    global mpu, i2c
    mpu = MPU6050(i2c)
    mpu.calibrate()


def setup_pwm():
    """Set up PWM for controlling the TFT backlight voltage during transition animations"""

    global pwm
    pwm = PWM(Pin(BACKLIGHT_PIN_NUM), freq=PWM_FREQ)
    pwm.duty(PWM_MAX_DUTY)


def mpu_read_isr(timer):
    """ISR for detecting motion using the MPU6050"""

    global shake_detected
    motion = mpu.is_moving()
    if motion:
        shake_detected = True
    else:
        shake_detected = False


def setup_mpu_read_timer():
    """
    Initialize a timer for taking periodic motion readings from the MPU6050

    Note:
        The MPU6050 must be configured for this timer and its corresponding ISR to work properly
    """

    global mpu_read_timer
    mpu_read_timer = Timer(MPU_READ_TIMER_NUM)
    mpu_read_timer.init(
        period=MPU_READ_PERIOD, mode=Timer.PERIODIC, callback=mpu_read_isr
    )


def draw_raw_image(filename):
    """
    Draw a pixel array image to the TFT display

    Args:
        filename: str, the relative or absolute path the raw pixel data to be drawn
    """

    global display
    with open(filename, "rb") as f:
        for y in range(320):
            line = f.read(240 * 2)  # 240 pixels * 2 bytes each
            display.block(0, y, 239, y, line)  # inclusive range: 0 to 239


def fade_out(duration_ms=1000, steps=20):
    """
    Dim the backlight to "fade out" the image

    Args:
        duration_ms: int, the duration of the transition
        steps: int, the number of steps to take when changing the PWM duty cycle
    """

    global pwm
    delay = duration_ms // steps
    for i in range(steps, -1, -1):
        pwm.duty(int(i * PWM_MAX_DUTY / steps))
        time.sleep_ms(delay)


def fade_in(duration_ms=1000, steps=20):
    """
    Brighten the backlight to "fade in" the image

    Args:
        duration_ms: int, the duration of the transition
        steps: int, the number of steps to take when changing the PWM duty cycle
    """

    global pwm
    delay = duration_ms // steps
    for i in range(0, steps + 1):
        pwm.duty(int(i * PWM_MAX_DUTY / steps))
        time.sleep_ms(delay)


def draw_next_image():
    """Draw the next image in the images array to the TFT display, transitioning with a fade-in/fade-out animation"""

    global current_pic_index

    fade_out()
    current_pic_index = (current_pic_index + 1) % len(IMAGE_FILENAMES)
    draw_raw_image(IMAGE_FILENAMES[current_pic_index])
    fade_in()


def main():

    global current_pic_index, shake_detected
    setup_spi()
    setup_i2c()
    setup_display()
    setup_mpu()
    setup_pwm()
    setup_mpu_read_timer()

    # draw the first image even before motion detected
    draw_raw_image(IMAGE_FILENAMES[current_pic_index])

    # draw new image when necessary outside of ISR since it would take too long
    while True:
        if shake_detected:
            shake_detected = False
            draw_next_image()

        # mercy for CPU
        time.sleep_ms(10)


main()
