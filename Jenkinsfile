pipeline {
    environment {
        dockerimagename = "bigjack213/food-app"

    }
    agent any
    triggers {
        pollSCM 'H/5 * * * *'
    }
    stages {
        stage('Checkout source control') {
            script {
                git credentialsId: 'github-credentials', url: 'https://github.com/JanKaczmarski/food-delivery.git'
            }
        }

        stage ('Build image') {
            steps {
                script {
                    def dockerImage = docker.build(dockerimagename, "./flask_app/")
                }
            }
        stage ('Push image') {
            environment {
                registryCredential = 'dockerhub-credentials'
            }
            steps {
                script {
                    docker.withRegistry( 'https://registry.hub.docker.com', registryCredential ) {
                        dockerImage.push("latest")
                    }
                }
            }
        }
        }
    }
}