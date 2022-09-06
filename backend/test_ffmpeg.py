import ffmpeg

videoInput = ffmpeg.input("./britz02-20220110-094000.wav")

videoOutput = videoInput.output("./test.wav")

videoOutput.run()


ffmpeg.input("./britz02-20220110-094000.wav", ss=5, to=15, v="error").output(
    "./test2.wav"
).run()

