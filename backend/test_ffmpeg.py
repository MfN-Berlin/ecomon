import ffmpeg

videoInput = ffmpeg.input("./test.mp4")

videoOutput = videoInput.output("./test.avi")

videoOutput.run()
