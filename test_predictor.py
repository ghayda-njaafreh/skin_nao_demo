from predictor import predict_image, build_speech_text

result = predict_image("example.png")
speech_text = build_speech_text(result)

print("RESULT:")
print(result)

print("\nSPEECH TEXT:")
print(speech_text)