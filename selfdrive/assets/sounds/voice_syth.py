from google.cloud import texttospeech

text = "CAR  RIGHT"

client = texttospeech.TextToSpeechClient()

input_text = texttospeech.SynthesisInput(text=text)

# Note: the voice can also be specified by name.
# Names of voices can be retrieved with client.list_voices().
voice = texttospeech.VoiceSelectionParams(
	language_code="en-US",
	name="en-US-Standard-C",
	ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
)

audio_config = texttospeech.AudioConfig(
	audio_encoding=texttospeech.AudioEncoding.WAV
)

response = client.synthesize_speech(
	request={"input": input_text, "voice": voice, "audio_config": audio_config}
)

# The response's audio_content is binary.
with open("output.wav", "wb") as out:
	out.write(response.audio_content)
	print('Audio content written to file "output.wav"')