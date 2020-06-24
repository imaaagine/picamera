import time
import picamera
import RPi.GPIO as GPIO
import sys, os, pyaudio, subprocess, wave

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.LOW)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
RECORD_SECONDS = 15
frames = []

try:
    with picamera.PiCamera() as camera:
	timestr = time.strftime("%y%m%d-%H%M%S")
	WAVE_OUTPUT_FILENAME = '/home/pi/Hyejin/Case1/' + timestr + '.wav'
	camera.start_preview(fullscreen=False, window=(930,0,425,295))
	GPIO.wait_for_edge(18, GPIO.FALLING)
	p = pyaudio.PyAudio()
	stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

	camera.start_recording('/home/pi/Hyejin/Case1/' + timestr + '.h264')
	GPIO.output(23, GPIO.HIGH)

        for i in range(0, int(RATE/CHUNK*RECORD_SECONDS)):
	    data = stream.read(CHUNK, exception_on_overflow = False)
	    frames.append(data)

	time.sleep(0.1)

	stream.stop_stream()
	stream.close()
	p.terminate()
	camera.stop_recording()
	camera.stop_preview()
	GPIO.output(23, GPIO.LOW)

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    os.execv(sys.executable, ['python']+sys.argv)

except KeyboardInterrupt:
	GPIO.output(23, GPIO.LOW)

finally:
	GPIO.cleanup()
