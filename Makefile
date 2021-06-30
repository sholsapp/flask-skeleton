deb:
	docker build -f Dockerfile --target builder -t sholsapp/flask-skeleton-builder .
	docker create --cidfile .tmp-docker-container-id sholsapp/flask-skeleton-builder
	xargs -I {} docker cp -a "{}:/build/flask-skeleton_0.1-1_amd64.deb" . < .tmp-docker-container-id
	xargs -I {} docker rm -f "{}" < .tmp-docker-container-id
	rm .tmp-docker-container-id

docker:
	docker build -t sholsapp/flask-skeleton:0.1 .
	docker run --cidfile .flask-skeleton-container-id --publish 5000:5000 --detach sholsapp/flask-skeleton:0.1

clean:
	git clean -fxd -e infra

