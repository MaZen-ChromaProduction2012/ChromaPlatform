CXX = g++
CXXFLAGS = -O3 -std=c++17 -Wall

all: compress video_info

compress: compress.cpp
	$(CXX) $(CXXFLAGS) compress.cpp -o compress

video_info: video_info.cpp
	$(CXX) $(CXXFLAGS) video_info.cpp -o video_info

clean:
	rm -f compress video_info
